from PIL import Image
import re #python module for regex
import pytesseract
# Manually specify the Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
from fuzzywuzzy import process
from datetime import date

# Known food database with estimated expiration times (days)
food_database = {
    "Milk": 7,
    "Organic Milk": 10,
    "Eggs": 21,
    "Chicken": 3,
    "Bread": 5,
    "Apples": 14
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
    print(text)
    print(" ---------------- ")
    
    # Clean text
    text = text.lower().strip()  # Convert to lowercase & trim spaces
    print(text)
    print(" ---------------- ")
    text = re.sub(r"(.+?)\s+\$?(\d+\.\d{2})", "", text)  # Remove special characters except . and $
    
    print(text)
    print(" ---------------- ")
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
    "cashier", "register","transaction"
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
    total_price = None
    date = None

    # Improved regex patterns
    item_price_pattern = r"([a-zA-Z\s\-]+)(?:\s+(\d+\.\d{2}))?"
    total_pattern = r"total\s*\$?(\d+\.\d{2})"
    date_pattern = r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"

    for line in lines:
        line = line.strip()
        print(f"Processing line: {line}")

        if is_header_line(line):
            print(f"Skipping header line: {line}")
            continue

        if has_ignore_words(line):
            print(f"Ignoring line: {line}")
            continue

        if is_footer_line(line):
            print(f"Reached footer, stopping processing: {line}")
            break

        item_match = re.search(item_price_pattern, line, re.IGNORECASE)
        if item_match:
            item_name = item_match.group(1).strip()
            price = item_match.group(3)  # Price may be None if not matched
            
            fuzzy_item_match = fuzzy_match(item_name)
            items.append({
                "item_name": item_name, 
                "match": fuzzy_item_match, 
                "price": float(price) if price else None
            })
            print(f"Item: {item_name}, Price: {price}, Fuzzy match: {fuzzy_item_match}")

    return items

