from PIL import Image
import re #python module for regex
import pytesseract
# Manually specify the Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
from fuzzywuzzy import process
from datetime import date
import pandas as pd

# Configuration
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load and prepare data
df = pd.read_csv("cleaned_shelf_life.csv")
food_database = {
    row["Name"]: [row["Pantry_shelf_life_days"], row["Refrigerator_shelf_life_days"], row["Freezer_shelf_life_days"]]
    for _, row in df.iterrows()
}
#used to match to current database. If theres a good enough match, it doesn't need to be run through the AI model
def fuzzy_match(item):
    best_match, score = process.extractOne(item, food_database.keys())
    if score > 80:  # Confidence threshold
        return best_match
    return None  # No suitable match

#used for image, image to text
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


ignore_keywords = [
    # grocery store names
    "trader joe's", "whole foods", "safeway", "walmart", "kroger", "costco",
    "publix", "aldi", "target", "meijer", "h-e-b", "wegmans", "albertsons",
    "food lion", "giant eagle", "stop & shop", "shoprite", "winn-dixie",
    "sam's club", "7-eleven", "cvs", "walgreens", "rite aid", "trader joe",

    # common terms
    "qty", "quantity", "price", "unit price", "item", "description",
    "upc", "sku", "barcode", "department", "dept", "category",
    "weight", "lb", "kg", "oz", "each", "ea", "discount"

    # Thank you msgs
    "thank you", "thanks for shopping", "come again", "visit us",
    "www", "com", "feedback", "survey", "opinion", "tell us",

    # Misc
    "open", "hours", "copyright", "all rights reserved",
    "printed", "duplicate", "copy", "original", "void",
    "cashier", "register","transaction","store",
]


def is_header_line(line):
    header_patterns = [
        r"\d{1,5}\s+[A-Za-z\s]+,\s+[A-Z]{2}\s+\d{5}",  # Address
        r"\d{3}-\d{3}-\d{4}",  # Phone number
        r"\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}",  # Date and time
    ]
    return any(re.match(pattern, line, re.IGNORECASE) for pattern in header_patterns)

def is_footer_line(line):
    footer_patterns = [
        r"subtotal",
        r"total",
        r"tax",
        r"credit",
        r"balance",
        r"payment",
        r"change due",
        r"items sold"
    ]
    return any(re.search(pattern, line, re.IGNORECASE) for pattern in footer_patterns)

def has_ignore_words(line):
    return any(keyword in line.lower() for keyword in ignore_keywords)

def extract_receipt_info(text):
    lines = text.split("\n")
    items = []

    # Improved regex patterns
    item_price_pattern = r"([a-zA-Z\s\-]+)(?:\s+(\d+\.\d{2}))?"

    for line in lines:
        line = line.strip()

        if is_header_line(line):
            continue

        if has_ignore_words(line):
            continue

        if is_footer_line(line):
            break

        item_match = re.search(item_price_pattern, line, re.IGNORECASE)
        if item_match:
            item_name = item_match.group(1).strip()
            
            fuzzy_item_match = fuzzy_match(item_name)
            items.append({
                "item_name": item_name, 
                "match": fuzzy_item_match, 
            })

    return items

