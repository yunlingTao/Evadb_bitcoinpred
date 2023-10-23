# from sqlalchemy import create_engine
# from statsmodels.tsa.arima.model import ARIMA
# import pandas as pd
# import pickle

# def train():
#     DATABASE_URL = "postgresql://eva:2021@localhost:5432/postgres_data"
#     engine = create_engine(DATABASE_URL)

#     query = "SELECT Date, Closing FROM BTC_USD ORDER BY Date"
#     df = pd.read_sql(query, engine)

#     df['Date'] = pd.to_datetime(df['date'])
#     df.set_index('Date', inplace=True)

#     df['closing'] = pd.to_numeric(df['closing'])
#     df.dropna(inplace=True)

#     p, d, q = 5, 1, 5
#     model = ARIMA(df['closing'], order=(p, d, q))
#     model_fit = model.fit()
#     # Save the trained model
#     with open('arima_bitcoin_model.pkl', 'wb') as model_file:
#         pickle.dump(model_fit, model_file)


# def forecast(days_to_forecast):
#     with open('arima_bitcoin_model.pkl', 'rb') as model_file:
#         model_fit = pickle.load(model_file)
        
#     forecast_values = model_fit.forecast(steps=days_to_forecast)
    
#     return list(forecast_values)

from sqlalchemy import create_engine
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import pandas as pd
import pickle

def stationarity_check(ts):
    result = adfuller(ts)
    if result[1] <= 0.05:
        return True
    else:
        return False

def train():
    DATABASE_URL = "postgresql://eva:2021@localhost:5432/postgres_data"
    engine = create_engine(DATABASE_URL)

    query = "SELECT Date, Closing FROM BTC_USD ORDER BY Date"
    df = pd.read_sql(query, engine)

    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    df['closing'] = pd.to_numeric(df['closing'])
    df.dropna(inplace=True)

    if not stationarity_check(df['closing']):
        df['Closing_diff'] = df['closing'].diff()
        df.dropna(inplace=True)

    p, d, q = 5, 1, 5  # You can consider optimizing these parameters.
    model = ARIMA(df['closing'], order=(p, d, q))
    model_fit = model.fit()

    # Save the trained model
    with open('arima_bitcoin_model.pkl', 'wb') as model_file:
        pickle.dump(model_fit, model_file)

def forecast(days_to_forecast):
    with open('arima_bitcoin_model.pkl', 'rb') as model_file:
        model_fit = pickle.load(model_file)
        
    # forecast_values = model_fit.forecast(steps=days_to_forecast)
    
    # return list(forecast_values)

    forecasts = []
    DATABASE_URL = "postgresql://eva:2021@localhost:5432/postgres_data"
    engine = create_engine(DATABASE_URL)
    query = "SELECT Date, Closing FROM BTC_USD ORDER BY Date"
    df = pd.read_sql(query, engine)
    data = df['closing'].tolist()

    for _ in range(days_to_forecast):
        model = ARIMA(data, order=(5, 1, 5))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=1)[0]
        forecasts.append(forecast)
        data.append(forecast)
    return forecasts

