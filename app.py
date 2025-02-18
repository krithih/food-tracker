from flask import Flask, request, jsonify
import os
from flask_cors import CORS #cors enables requests from different port origins
import cv2
import numpy as np
from extract_info import *
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
from expiration_prediction import *


app = Flask(__name__)
CORS(app, resources={r"/upload": {"origins": "http://localhost:5500"}})

# Configure SQLite database (you can use PostgreSQL or MySQL instead)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food_expiration.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define database model to store 
class FoodItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    match = db.Column(db.String(100))
    pantry_life = db.Column(db.Integer)
    refrigerator_life = db.Column(db.Integer)
    freezer_life = db.Column(db.Integer)

    def __repr__(self):
        return f"<FoodItem {self.item_name}>"


# Create the database
with app.app_context():
    db.create_all()

# Define upload folder
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)  # Create folder if it doesn't exist

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Allow only image file types 
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to handle file upload

@app.route("/upload", methods=["POST"])
def upload_file():
    print("Received a request!")  # Debugging: Check if request reaches Flask
    print("Request form data:", request.form)  
    print("Request files data:", request.files)

    if "file" not in request.files:
        print("No file part")  # Debugging line
        return jsonify({"message": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        print("No selected file")  # Debugging line
        return jsonify({"message": "No selected file"}), 400

    if file and allowed_file(file.filename):
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        print(f"Saving to: {file_path}")
        file.save(file_path)

        # Call OCR function to extract text
        extracted_text = extract_text(file_path)
        print(f"Extracted text: {extracted_text}")

        if not extracted_text:
            print("No text extracted from the image")
            return jsonify({"message": "Failed to extract text from image"}), 400
      

        # process the text, predict the shelf life, and save to database
        process_receipt_and_save(extracted_text)

        return jsonify({
            "message": f"File {file.filename} uploaded successfully!",
            "extracted_text": extracted_text
        }), 200

    print("Invalid file type")  # Debugging line
    return jsonify({"message": "Invalid file type"}), 400

#function that saves 
def save_to_db(item_data):
    new_item = FoodItem(
        item_name=item_data["item_name"],
        match=item_data["match"],
        pantry_life=item_data["predicted_expiration"]["Pantry Life"],
        refrigerator_life=item_data["predicted_expiration"]["Refrigerator Life"],
        freezer_life=item_data["predicted_expiration"]["Freezer Life"]
    )

    db.session.add(new_item)
    db.session.commit()
    print(f"Saved {item_data['item_name']} to the database.")

# Initialize the predictor once
expiration_predictor = ExpirationPredictor()
def process_receipt_and_save(text):
    receipt_data = extract_receipt_info(text) 

    for item in receipt_data["items"]:
        predicted_shelf_life = expiration_predictor.predict_expiration(item["item_name"], item["match"])
        expiration_data = {
            "item_name": item["item_name"],
            "match": item["match"],
            "pantry life" : predicted_shelf_life["Pantry Life"],
            "refridgerator life" : predicted_shelf_life["Refridgerator Life"],
            "pantry life" : predicted_shelf_life["Pantry Life"]
        }
        save_to_db(expiration_data)



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


    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

