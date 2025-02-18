# Imports
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import *
import math

# Custom module imports
from extract_info import extract_text, extract_receipt_info
from expiration_prediction import ExpirationPredictor

# Flask app initialization
app = Flask(__name__)
CORS(app, resources={r"/upload": {"origins": "http://localhost:5500"}})

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food_expiration.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#food class
class FoodItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    match = db.Column(db.String(100), nullable=True)
    pantry_life = db.Column(db.Integer)
    refrigerator_life = db.Column(db.Integer)
    freezer_life = db.Column(db.Integer)
    pantry_expiration = db.Column(db.DateTime, nullable=True)
    refrigerator_expiration = db.Column(db.DateTime, nullable=True)
    freezer_expiration = db.Column(db.DateTime, nullable=True)

    def __init__(self, item_name, match, pantry_life, refrigerator_life, freezer_life):
        self.item_name = item_name
        self.match = match
        self.pantry_life = pantry_life
        self.refrigerator_life = refrigerator_life
        self.freezer_life = freezer_life
        self.date_bought = datetime.now(timezone.utc)

        if pantry_life is not None and not math.isnan(pantry_life):
            self.pantry_expiration = self.date_bought + timedelta(days=int(pantry_life))
        else:
            self.pantry_expiration = None 

        if refrigerator_life is not None and not math.isnan(refrigerator_life):
            self.refrigerator_expiration = self.date_bought + timedelta(days=int(refrigerator_life))
        else:
            self.refrigerator_expiration = None  

        if freezer_life is not None and not math.isnan(freezer_life):
            self.freezer_expiration = self.date_bought + timedelta(days=int(freezer_life))
        else:
            self.freezer_expiration = None  

# Create the database
with app.app_context():
    db.create_all()

# File upload configuration
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# Initialize the predictor
expiration_predictor = ExpirationPredictor()

# Helper functions
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def save_to_db(item_data):
    new_item = FoodItem(
        item_name=item_data["item_name"],
        match=item_data["match"],
        pantry_life=item_data["pantry_life"],
        refrigerator_life=item_data["refrigerator_life"],
        freezer_life=item_data["freezer_life"]
    )
    db.session.add(new_item)
    db.session.commit()
    print(f"Saved {item_data['item_name']} to the database.")

def process_receipt_and_save(text):
    print("I am working")

    receipt_data = extract_receipt_info(text) 
    print(receipt_data)
    for item in receipt_data:
        print(item)
        predicted_shelf_life = expiration_predictor.predict_expiration(item["item_name"], item["match"])
        expiration_data = {
            "item_name": item["item_name"],
            "match": item["match"],
            "pantry_life": predicted_shelf_life["Pantry Life"],
            "refrigerator_life": predicted_shelf_life["Refrigerator Life"],
            "freezer_life": predicted_shelf_life["Freezer Life"]
        }
        save_to_db(expiration_data)

# Routes
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"message": "No selected file"}), 400

    if file and allowed_file(file.filename):
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)

        extracted_text = extract_text(file_path)
        if not extracted_text:
            return jsonify({"message": "Failed to extract text from image"}), 400

        process_receipt_and_save(extracted_text)

        return jsonify({
            "message": f"File {file.filename} uploaded successfully!",
            "extracted_text": extracted_text
        }), 200

    return jsonify({"message": "Invalid file type"}), 400

@app.route("/food-items", methods=["GET"])
def get_food_items():
    items = FoodItem.query.all()
    return jsonify([
        {
            "item_name": item.item_name,
            "match": item.match,
            "pantry_life": item.pantry_life,
            "refrigerator_life": item.refrigerator_life,
            "freezer_life": item.freezer_life
        }
        for item in items
    ])

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
