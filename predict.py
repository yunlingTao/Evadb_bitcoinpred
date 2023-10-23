import pandas as pd
from sqlalchemy import create_engine
from load_data import load
from train_model import train, forecast
from sklearn.metrics import mean_squared_error


def predict(date_str):
    load()
    train()
    
    future_date = pd.to_datetime(date_str)
    
    DATABASE_URL = "postgresql://eva:2021@localhost:5432/postgres_data"
    engine = create_engine(DATABASE_URL)
    last_date_in_db = pd.read_sql("SELECT MAX(Date) as last_date FROM BTC_USD", engine)["last_date"].iloc[0]
    days_to_forecast = (future_date.date() - last_date_in_db).days
    
    if days_to_forecast <= 0:
        print("Please provide a future date.")
        return
    forecast_val = forecast(days_to_forecast)
    print(forecast_val)
    
    predicted_price = forecast_val[-1]
    
    print(f"Predicted Bitcoin Price for {date_str}: ${predicted_price:.2f}")
    
