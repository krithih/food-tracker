from fuzzywuzzy import process
from extract_info import *
import re

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder


#sample extracted text
sample_extracted_text = "Milk          $3.99\nEggs          $7.00        \nChken pot pie           $5.99"
sample_extracted_text = sample_extracted_text.lower().strip()

# Example OCR output
processed_items = extract_receipt_info(sample_extracted_text)


# Known food database with estimated expiration times (days)
food_database = {
    "Milk": 7,
    "Organic Milk": 10,
    "Eggs": 21,
    "Chicken": 3,
    "Bread": 5,
    "Apples": 14
}


# Sample dataset
data = {
    "Item": ["Milk", "Organic Milk", "Eggs", "Chicken", "Bread", "Apples"],
    "Price": [4.99, 5.99, 3.49, 7.99, 2.99, 3.99],
    "Days_Until_Expiry": [7, 10, 21, 3, 5, 14]
}

df = pd.DataFrame(data)
print(df.head())

#Apply One-Hot Encoding to Item Names, this is necessary because models don't handle raw text efficiently
encoder = OneHotEncoder(sparse_output=False)
one_hot_encoded = encoder.fit_transform(df[["Item"]])

# Convert to DataFrame and merge
encoded_df = pd.DataFrame(one_hot_encoded, columns=encoder.get_feature_names_out(["Item"]))
df = pd.concat([df, encoded_df], axis=1).drop(columns=["Item"])


# Train model
X = df.drop(columns=["Days_Until_Expiry"])
y = df["Days_Until_Expiry"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestRegressor()
model.fit(X_train, y_train)

# Predict expiration for extracted items
def predict_expiration(name, price,match):
    
    if match in food_database:
        return food_database[match]  # Use stored values if available

    # Encode the matched item name using the fitted one-hot encoder
    item_encoded = encoder.transform([[match]]) if match in encoder.categories_[0] else [[0] * len(encoder.categories_[0])]

    # Merge price with encoded item features
    features = [[price] + list(item_encoded[0])]
    return model.predict(features)[0]

# Predict for processed receipt items
for item in processed_items:
    item["predicted_expiration"] = int(predict_expiration(item["item_name"], item["price"],item["match"]))

print(processed_items)

