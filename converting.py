import json
import pandas as pd
'''
This file was used to convert the JSON File I downloaded from the USDA website to a csv, so it was easier for the AI model to read it
**Only runs once
food_data.json ---> test.csv
'''
# Open JSON file
with open('food_data.json', encoding="utf8") as f:
    data = json.load(f)  # data is a list of lists of dictionaries

# Initialize lists
id_names = []
category_ID = []
item_names = []
keywords = []
pantry = []
pantry_metric = []
refrigerate = []
refrigerate_metric = []
freeze = []
freeze_metric = []

# Iterate through each list in JSON data
for food_list in data:  # food_list is a list of dictionaries
    food_dict = {entry_key: entry_val for d in food_list for entry_key, entry_val in d.items()}  # Flatten each food list into a dictionary
    
    # Extracting values
    id_names.append(int(food_dict.get("ID", 0)))  # Default to 0 if ID is missing
    category_ID.append(int(food_dict.get("Category_ID", 0)))  # Default to 0 if missing

    # Append name with subtitle if available
    name = food_dict.get("Name", "")
    name_subtitle = food_dict.get("Name_subtitle")
    item_names.append(f"{name} ({name_subtitle})" if name_subtitle else name)

    keywords.append(food_dict.get("Keywords", ""))  # Default to empty string if missing

    # Pantry shelf life
    if food_dict.get("Pantry_Max") is not None:
        pantry.append(int(food_dict["Pantry_Max"]))
        pantry_metric.append(food_dict.get("Pantry_Metric"))
    elif food_dict.get("DOP_Pantry_Max") is not None:
        pantry.append(int(food_dict["DOP_Pantry_Max"]))
        pantry_metric.append(food_dict.get("DOP_Pantry_Metric"))
    else:
        pantry.append(None)
        pantry_metric.append(None)

    # Refrigerate shelf life
    if food_dict.get("Refrigerate_Max") is not None:
        refrigerate.append(int(food_dict["Refrigerate_Max"]))
        refrigerate_metric.append(food_dict.get("Refrigerate_Metric"))
    elif food_dict.get("DOP_Refrigerate_Max") is not None:
        refrigerate.append(int(food_dict["DOP_Refrigerate_Max"]))
        refrigerate_metric.append(food_dict.get("DOP_Refrigerate_Metric"))
    else:
        refrigerate.append(None)
        refrigerate_metric.append(None)

    # Freeze shelf life
    if food_dict.get("Freeze_Max") is not None:
        freeze.append(int(food_dict["Freeze_Max"]))
        freeze_metric.append(food_dict.get("Freeze_Metric"))
    elif food_dict.get("DOP_Freeze_Max") is not None:
        freeze.append(int(food_dict["DOP_Freeze_Max"]))
        freeze_metric.append(food_dict.get("DOP_Freeze_Metric"))
    else:
        freeze.append(None)
        freeze_metric.append(None)

# Debugging: Check list lengths
print("ID length:", len(id_names))
print("Category_ID length:", len(category_ID))
print("Name length:", len(item_names))
print("Keywords length:", len(keywords))
print("Pantry_shelf_life length:", len(pantry))
print("Pantry_metric length:", len(pantry_metric))
print("Refrigerator_shelf_life length:", len(refrigerate))
print("Refrigerator_metric length:", len(refrigerate_metric))
print("Freezer_shelf_life length:", len(freeze))
print("Freezer_metric length:", len(freeze_metric))

# Convert to dictionary and create DataFrame
new_dict = {
    "ID": id_names, 
    "Category_ID": category_ID, 
    "Name": item_names, 
    "Keywords": keywords, 
    "Pantry_shelf_life": pantry, 
    "Pantry_metric": pantry_metric, 
    "Refrigerator_shelf_life": refrigerate, 
    "Refrigerator_metric": refrigerate_metric, 
    "Freezer_shelf_life": freeze, 
    "Freezer_metric": freeze_metric
}

df = pd.DataFrame(new_dict)

# Save to CSV
df.to_csv("test.csv", index=False)

print("CSV file created")
