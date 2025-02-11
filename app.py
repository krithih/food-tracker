
from flask import Flask, request, jsonify
import os
from flask_cors import CORS #cors enables requests from different port origins
import pytesseract
# Manually specify the Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

from PIL import Image
import cv2
import numpy as np
 
import re #python module for regex


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
        print(extracted_text)
      

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


def extract_text(image_path):
    # Open image using PIL
    image = Image.open(image_path)

    # Convert image to grayscale for better OCR accuracy
    image = image.convert("L")  # Convert to grayscale

    # Apply OCR
    text = pytesseract.image_to_string(image)
    
    # Clean text
    text = text.lower().strip()  # Convert to lowercase & trim spaces
    text = re.sub(r"(.+?)\s+\$?(\d+\.\d{2})", "", text)  # Remove special characters except . and $
    return text
    
    
def extract_receipt_info(text):
    lines = text.split("\n")
    items = []
    total_price = None
    date = None

    item_price_pattern = r"([a-z\s]+)\s+\$?(\d+\.\d{2})"
    total_pattern = r"total\s*\$?(\d+\.\d{2})"
    date_pattern = r"\d{1,2}/\d{1,2}/\d{2,4}"

    for line in lines:
        line = line.strip()
        print(f"Processing line: {line}")

        item_match = re.search(item_price_pattern, line)
        if item_match:
            item_name = item_match.group(1).strip()
            price = item_match.group(2)
            items.append({"item": item_name, "price": price})
            print(f"Matched item: {item_name}, price: {price}")

        total_match = re.search(total_pattern, line, re.IGNORECASE)
        if total_match:
            total_price = total_match.group(1)
            print(f"Matched total: {total_price}")

        date_match = re.search(date_pattern, line)
        if date_match:
            date = date_match.group()
            print(f"Matched date: {date}")

    return {
        "items": items,
        "total_price": total_price,
        "date": date
    }


    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

