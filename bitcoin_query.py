import pandas as pd
from sqlalchemy import create_engine, text
from predict import predict
from datetime import datetime
import psycopg2

DATABASE_URL = "postgresql://eva:2021@localhost:5432/postgres_data"
engine = create_engine(DATABASE_URL)

    
def get_historical_data(date):
    try:
        query = f"SELECT * FROM BTC_USD WHERE Date = '{date}' ORDER BY Date ASC"
        df = pd.read_sql(query, engine)
        if not df.empty:
            return df.iloc[0], True
        else:
            return "No data found for this date", False
    except ValueError:
        return "Not a correct date format.", False
 
def add_modify_data(date, currency, closing, open, high, low):
    DATABASE_URL = "postgresql://eva:2021@localhost:5432/postgres_data"
    engine = create_engine(DATABASE_URL)

    existing_data, b = get_historical_data(date)
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()
    if b:
        query = text("""
            UPDATE BTC_USD SET Currency=:currency, Closing=:closing, Open=:open, High=:high, Low=:low
            WHERE Date = :date
        """)
    else:
        query = text("""
            INSERT INTO BTC_USD (Currency, Date, Closing, Open, High, Low)
            VALUES (:currency, :date, :closing, :open, :high, :low)
        """)
    
    connection = engine.connect()
    query = query.bindparams(currency=currency, date=date, closing=closing, open=open, high=high, low=low)
    result = connection.execute(query)
    connection.commit()
    connection.close()
    
def delete_data(date):
    query = text("""
        DELETE FROM BTC_USD WHERE Date = :date
    """)
    
    connection = engine.connect()

    query = query.bindparams(date=date)

    result = connection.execute(query)

    connection.commit()
    connection.close()


def main():
    action = input("Enter action (forecast, retrieve, add, modify, delete): ").strip().lower()

    if action == "forecast":
        date_str = input("Enter the date (YYYY-MM-DD) for which you want to forecast the Bitcoin price: ")
        predict(date_str)

    elif action == "retrieve":
        date_str = input("Enter the date (YYYY-MM-DD) you want data for: ")
        
        data, b = get_historical_data(date_str)
        if b:
            print(data)
        

    elif action in ["add", "modify"]:
        date = input("Enter the date (YYYY-MM-DD): ")
        currency = input("Enter the currency (e.g., BTC_USD): ")
        closing = float(input("Enter the closing price: "))
        open_price = float(input("Enter the opening price: "))
        high = float(input("Enter the high price: "))
        low = float(input("Enter the low price: "))
        add_modify_data(date, currency, closing, open_price, high, low)

    elif action == "delete":
        date = input("Enter the date (YYYY-MM-DD) you want to delete data for: ")
        delete_data(date)
    else:
        print("Invalid action.")

if __name__ == "__main__":
    main()
