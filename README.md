Title: AI-powered Food Waste Tracker

Overview
This project is an AI-powered food waste tracker that predicts food expiration dates based on extracted receipt information. The system uses machine learning models to analyze food items and determine their shelf life in the pantry, fridge, and freezer.

Features
1. Interactive web interface with Flask (Backend) and HTML/CSS/JavaScript (Frontend).
2. Upload a receipt image to extract food item details.
3. An OCR extracts the text and an extraction function filters receipt information from the text.
4. AI models predict expiration dates for pantry, refrigerator, and freezer storage.
5. Stores and retrieves food data using SQLite.

Project Structure
📂 instance/ → Contains SQLite database files.
📂 uploads/ → Stores uploaded receipt images.
📄 app.py → Main Flask application that handles requests.
📄 cleaned_shelf_life.csv → Preprocessed shelf-life data for food items.
📄 clear_database.py → running it once clears food_expiration.db completely
📄 converting.py → Converts JSON data from the USDA website into the correct format (csv) for processing without altering any data.
📄 expiration_prediction.py → AI model for predicting expiration dates.
📄 extract_info.py → Extracts food item details from uploaded receipts.
📄 food_data.json → Stores food item data in JSON format.
📄 freezer_model.pkl / fridge_model.pkl / pantry_model.pkl → Machine learning models for predicting expiration dates.
📄 index.html → Web interface for uploading receipts.
📄 preprocessing_data.py → Handles preprocessing before storing data, standardizing the shelf lives into a metric of days
📄 script.js → Frontend logic to interact with Flask API.
📄 style.css → Styles for the web interface.
📄 test.csv → Sample food data in CSV format.

Installation & Setup
1. Ensure Python is installed
2. Install these libraries: pip install flask flask-sqlalchemy flask-cors pandas numpy pytesseract scikit-learn fuzzywuzzy python-Levenshtein joblib pillow
3. To properly use pytesseract, edit environment variables, add path: C:\Program Files\Tesseract_OCR\tesseract.exe (for Windows)
3. Run the Flask App: python app.py
The server will start at http://127.0.0.1:5000/
4. Upload a Receipt
Go to index.html in your browser.
Upload an image of a receipt.
The system will extract items and predict expiration dates.

API Endpoints
Method Endpoint	Description
POST	/upload	Uploads a receipt image for processing.
GET	/food-items	Retrieves stored food item details in JSON format.

Future Improvements
1. Improve OCR accuracy for better receipt parsing, consider using Google Cloud Vision API
2. Implement an AI model that is specifically designed for NLP tasks to get better accuracy in predictions
2. Create a user login system to keep track of foods per household.
3. Add an editing method so the user can edit when the items were bought, or change the shelf life data if the prediction model got it wrong.

Contributors
Krithi H 
