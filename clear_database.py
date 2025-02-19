'''This file runs to clear the items from the database. It was extremely useful in cleaning the data when I wanted to upload the same receipt multiple times'''
from app import app,db, FoodItem  #flask app instance, database, and foodItem class

with app.app_context():  
    db.session.query(FoodItem).delete()  # Deletes all rows in the table
    db.session.commit()  # Saves changes

print("All food items have been deleted from the database.")
