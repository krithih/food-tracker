
from flask import Flask, request, jsonify
import os
from flask_cors import CORS #cors enables requests from different port origins
import cv2
import numpy as np
from extract_info import *



app = Flask(__name__)
CORS(app, resources={r"/upload": {"origins": "http://localhost:5500"}})


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
      

        # Process the text to extract structured info
        receipt_info = extract_receipt_info(extracted_text)
        print(receipt_info)

        return jsonify({
            "message": f"File {file.filename} uploaded successfully!",
            "extracted_text": extracted_text,
            "receipt_info": receipt_info
        }), 200

    print("Invalid file type")  # Debugging line
    return jsonify({"message": "Invalid file type"}), 400



    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

