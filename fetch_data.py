import requests
import pandas as pd
import sqlite3
import time

# This function is used to get data from the Fake Store API
def fetch_data():
    try:
        print("Fetching data...")
        response = requests.get("https://fakestoreapi.com/products", timeout=10)
        response.raise_for_status()  # This checks if the request worked fine
        data = response.json()
        print("Data fetched successfully.")
        return data
    except Exception as e:
        print("There was a problem while fetching data:", e)
        # If something goes wrong, save the error in a file
        with open("error.log", "a") as f:
            f.write(f"{time.ctime()} - Error: {e}\n")
        return []

# This function cleans and prepares the data before saving
def transform_data(data):
    print("Changing the data format...")
    df = pd.DataFrame(data)

    # Change some column names to make them easy to understand
    df = df.rename(columns={"title": "product_name", "price": "price_usd"})

    # Add a new column that shows the price in Indian Rupees
    df["price_in_inr"] = df["price_usd"] * 85

    # Some data has 'rating' stored as a dictionary, so we separate it
    if "rating" in df.columns:
        df["rating_rate"] = df["rating"].apply(lambda x: x.get("rate") if isinstance(x, dict) else None)
        df["rating_count"] = df["rating"].apply(lambda x: x.get("count") if isinstance(x, dict) else None)
        df = df.drop(columns=["rating"])

    print("Data format changed successfully.")
    return df

# This function saves all the data into a small local database
def store_data(df):
    print("Saving data into the database...")
    conn = sqlite3.connect("store.db")
    # If the table already exists, replace it with new data
    df.to_sql("products", conn, if_exists="replace", index=False)
    conn.close()
    print("Data saved in store.db")

# This function writes the date and time when everything worked fine
def log_success():
    with open("pipeline_status.txt", "w") as f:
        f.write(f"Last run completed successfully on: {time.ctime()}\n")

# This is the main part where all steps are called one by one
if __name__ == "__main__":
    data = fetch_data()
    if data:
        df = transform_data(data)
        store_data(df)
        log_success()
        print("All steps done successfully.")
    else:
        print("Something went wrong — please check error.log")
