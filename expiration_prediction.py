from fuzzywuzzy import process
from extract_info import *
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
import joblib  # For saving and loading models



class ExpirationPredictor:
    def __init__(self, csv_file="cleaned_shelf_life.csv"):
        self.df = pd.read_csv(csv_file)

        # Create food database dictionary
        self.food_database = {
            row["Name"]: [row["Pantry_shelf_life_days"], row["Refrigerator_shelf_life_days"], row["Freezer_shelf_life_days"]]
            for _, row in self.df.iterrows()
        }

        # One-Hot Encoding
        self.encoder = OneHotEncoder(sparse_output=False)
        one_hot_encoded = self.encoder.fit_transform(self.df[["Name"]])

        encoded_df = pd.DataFrame(one_hot_encoded, columns=self.encoder.get_feature_names_out(["Name"]))
        self.df = pd.concat([self.df, encoded_df], axis=1).drop(columns=["Name"])

        # Prepare target variables
        self.y_pantry = self.df["Pantry_shelf_life_days"]
        self.y_fridge = self.df["Refrigerator_shelf_life_days"]
        self.y_freezer = self.df["Freezer_shelf_life_days"]

        self.X_pantry, self.y_pantry = encoded_df[self.y_pantry.notna()], self.y_pantry.dropna()
        self.X_fridge, self.y_fridge = encoded_df[self.y_fridge.notna()], self.y_fridge.dropna()
        self.X_freezer, self.y_freezer = encoded_df[self.y_freezer.notna()], self.y_freezer.dropna()

        # Train models
        self.pantry_model = self.train_model(self.X_pantry, self.y_pantry, "pantry_model.pkl")
        self.fridge_model = self.train_model(self.X_fridge, self.y_fridge, "fridge_model.pkl")
        self.freezer_model = self.train_model(self.X_freezer, self.y_freezer, "freezer_model.pkl")

    def train_model(self, X, y, model_filename):  
        """Train or load a model to avoid retraining"""
        try:
            model = joblib.load(model_filename)  # Load saved model if available
            print(f"Loaded {model_filename} from disk.")
        except FileNotFoundError:      #if the .pkl files don't exist
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)
            joblib.dump(model, model_filename)  # Save model for future use
            print(f"Trained and saved {model_filename}.")
        return model

    def predict_expiration(self, name, match):
        if match in self.food_database:  #if there is a match to the food in cleaned_shelf_life.csv, Ex: mustard, then food doesn't need to go through the model
            return {
                "Pantry Life": self.food_database[match][0],
                "Refrigerator Life": self.food_database[match][1],
                "Freezer Life": self.food_database[match][2]
            }

        item_encoded = self.encoder.transform([[match]]) if match in self.encoder.categories_[0] else [[0] * len(self.encoder.categories_[0])]

        pantry_life = int(self.pantry_model.predict(item_encoded)[0])
        refrigerator_life = int(self.fridge_model.predict(item_encoded)[0])
        freezer_life = int(self.freezer_model.predict(item_encoded)[0])

        return {
            "Pantry Life": pantry_life,
            "Refrigerator Life": refrigerator_life,
            "Freezer Life": freezer_life
        }
