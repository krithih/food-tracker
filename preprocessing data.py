import pandas as pd
import numpy as np

def convert_to_days(value, metric):
    """Converts shelf life values to days based on their metric."""
    if pd.isna(value) or pd.isna(metric):
        return np.nan  # Keep NaN values for missing entries
    
    conversion_factors = {
        'Days': 1,
        'Weeks': 7,
        'Months': 30  
    }
    
    return value * conversion_factors.get(metric, 1)  # Default to 1 if metric is unexpected

# Load the CSV file
df = pd.read_csv("test.csv")  

# Apply conversion to pantry, refrigerator, and freezer shelf life columns
df["Pantry_shelf_life_days"] = df.apply(lambda row: convert_to_days(row["Pantry_shelf_life"], row["Pantry_metric"]), axis=1)
df["Refrigerator_shelf_life_days"] = df.apply(lambda row: convert_to_days(row["Refrigerator_shelf_life"], row["Refrigerator_metric"]), axis=1)
df["Freezer_shelf_life_days"] = df.apply(lambda row: convert_to_days(row["Freezer_shelf_life"], row["Freezer_metric"]), axis=1)

# Drop old columns
df.drop(columns=["Pantry_shelf_life", "Pantry_metric", "Refrigerator_shelf_life", "Refrigerator_metric", "Freezer_shelf_life", "Freezer_metric"], inplace=True)

# Save the cleaned file
df.to_csv("cleaned_shelf_life.csv", index=False)

print("Preprocessing complete")
