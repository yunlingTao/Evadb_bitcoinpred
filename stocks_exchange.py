import warnings
import os
import openai
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import yfinance as yf
import pandas_ta as pta
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

warnings.filterwarnings("ignore")

os.environ['OPENAI_KEY'] = 'sk...'
open_ai_key = os.environ.get('OPENAI_KEY')
openai.api_key = open_ai_key

connection = sqlite3.connect('evadb.db')
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS stock_data (
    date TEXT PRIMARY KEY,
    open_price FLOAT,
    high_price FLOAT,
    low_price FLOAT,
    close_price FLOAT,
    volume INTEGER
);
""")
connection.commit()

# load BTC data from CSV
def load_btc_data(csv_file):
    btc_data = pd.read_csv(csv_file)
    try: # convert date column if in MM/DD/YY
        btc_data['Date'] = pd.to_datetime(btc_data['Date'], format='%m/%d/%y')
    except ValueError: 
        try: # assume YYYY-MM-DD
            btc_data['Date'] = pd.to_datetime(btc_data['Date'], format='%Y-%m-%d')
        except ValueError:
            raise ValueError("Date column is not in a recognized format that can be converted to YYYY-MM-DD.")
    
    # Convert to format YYYY-MM-DD
    btc_data['Date'] = btc_data['Date'].dt.strftime('%Y-%m-%d')
    
    btc_data.to_sql('stock_data', connection, if_exists='replace', index=False)


def get_stock_data_for_date(date):
    query = f"SELECT * FROM stock_data WHERE date = '{date}';"
    return pd.read_sql_query(query, connection)

# 14 days before 
def get_pre_start_date(start_date_str): 
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    pre_start_date = start_date - timedelta(days=14)
   
    pre_start_date_str = pre_start_date.strftime('%Y-%m-%d')
    return pre_start_date_str

def scrape_and_store_btc_data(start, end):
    btc = "BTC-USD"
    btc_data = yf.download(btc, start=start, end=end)

    rsi = pta.rsi(btc_data["Close"], length=14)
    obv = pta.obv(btc_data["Close"], btc_data["Volume"])

    btc_data["RSI"] = rsi
    btc_data["OBV"] = obv

    btc_data.reset_index(inplace=True)
    btc_data['Date'] = btc_data['Date'].dt.strftime('%Y-%m-%d')
    btc_data.drop(index=btc_data.index[:14], axis=0, inplace=True)

    btc_data.reset_index(drop=True, inplace=True)
    data_list = btc_data.to_dict('records')
    return data_list


def modify_stock_data(start_date, end_date):
    # Scrape the data within the given date range
    start_date = get_pre_start_date(start_date)
    btc_data_list = scrape_and_store_btc_data(start_date, end_date)
    
    for data in btc_data_list:
        currency = 'BTC'
        date = data['Date']
        closing = data['Close']
        open_price = data['Open']
        high = data['High']
        low = data['Low']
        
        # Check if the date already exists in the database
        cursor.execute("""
        SELECT EXISTS(SELECT 1 FROM stock_data WHERE date = ?)
        """, (date,))
        exists = cursor.fetchone()[0]
        
        # If  exist, insert new data
        if not exists:
            cursor.execute("""
            INSERT INTO stock_data (currency, date, closing, open, high, low) 
            VALUES (?, ?, ?, ?, ?, ?)
            """, (currency, date, closing, open_price, high, low))
    connection.commit()

def summarize_stock_data(start_date, end_date):
    query = f"SELECT * FROM stock_data WHERE date BETWEEN '{start_date}' AND '{end_date}';"
    data = pd.read_sql_query(query, connection)
    summary_prompt = f"Summarize this stock data trend in detail:\n{data.to_string(index=False)}"
    
    summary = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are an assistant who summarizes stock data trends."},
                  {"role": "user", "content": summary_prompt}]
    )
    
    return summary['choices'][0]['message']['content'].strip()

def plot_data_distribution(start_date, end_date):
    
    if start_date is None or end_date is None:
        print("Invalid date format provided.")
        return

    query = f"""
    SELECT * FROM stock_data 
    WHERE date BETWEEN '{start_date}' AND '{end_date}'
    """
    data = pd.read_sql_query(query, connection)
    data = data.select_dtypes(include=[np.number])

    for column in data.columns:
        plt.figure(figsize=(10, 6))
        sns.histplot(data[column], kde=True)
        plt.title(f'Distribution of {column} between {start_date} and {end_date}')
        plt.xlabel(column)
        plt.ylabel('Frequency')
        plt.show()

# def plot_closing_price_vs_date(start_date, end_date):
    
#     if start_date is None or end_date is None:
#         print("Invalid date format provided.")
#         return

#     query = f"""
#     SELECT * FROM stock_data 
#     WHERE date BETWEEN '{start_date}' AND '{end_date}'
#     """
#     data = pd.read_sql_query(query, connection)
#     data = data.select_dtypes(include=[np.number])

#     # Plot the closing prices against the dates
#     plt.figure(figsize=(14, 7))
#     plt.plot(data['date'], data['closing'], marker='o', linestyle='-', color='blue')
#     plt.title('Closing Price vs. Date')
#     plt.xlabel('Date')
#     plt.ylabel('Closing Price')
#     plt.grid(True)
#     plt.xticks(rotation=45)
#     plt.tight_layout()
#     plt.show()
    
def show_db_snapshot(start_date, end_date):
    if start_date is None or end_date is None:
        print("Invalid date format provided.")
        return

    query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = pd.read_sql_query(query, connection)

    for table in tables['name']:
        print(f"\nSnapshot of table '{table}' between {start_date} and {end_date}:")
        table_query = f"""
        SELECT * FROM {table}
        WHERE date BETWEEN '{start_date}' AND '{end_date}';
        """
        table_data = pd.read_sql_query(table_query, connection)
        print(table_data)


def train_random_forest_model():

    query = "SELECT * FROM stock_data"
    data = pd.read_sql_query(query, connection)

    data['Date'] = pd.to_datetime(data['Date'])
    data.sort_values('Date', inplace=True)

    features = data[['Open', 'High', 'Low']]
    target = data['Closing']

    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    return model

def predict_closing_price(model):
    query = "SELECT * FROM stock_data"
    data = pd.read_sql_query(query, connection)
    most_recent_data = data.iloc[-1][['Open', 'High', 'Low']].values.reshape(1, -1)
    
    predicted_closing_price = model.predict(most_recent_data)
    return predicted_closing_price[0]



load_btc_data('./content/BTC_USD.csv')

def main():
    while True:
        print("\nMenu:")
        print("1. Get stock data for a specific date")
        print("2. Modify stock data")
        print("3. Predict future stock price")
        print("4. Summarize stock data")
        print("5. Show data distribution plot")
        print("6. Show database snapshot")
        print("7. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            date = input("Enter the date (YYYY-MM-DD): ")
            data = get_stock_data_for_date(date)
            print(data)

        elif choice == '2':
            start_date = input("Enter the start date (YYYY-MM-DD): ")
            end_date = input("Enter the end date (YYYY-MM-DD): ")
            modify_stock_data(start_date, end_date)
            print("Stock data updated.")
            show_db_snapshot(start_date, end_date)

        elif choice == '3':
            rf_model = train_random_forest_model()
            predicted_price = predict_closing_price(rf_model)
            print(f"Predicted closing price for {predicted_price}")

        elif choice == '4':
            start_date = input("Enter start date (YYYY-MM-DD): ")
            end_date = input("Enter end date (YYYY-MM-DD): ")
            summary = summarize_stock_data(start_date, end_date)
            print(summary)

        elif choice == '5':
            start_date = input("Enter start date (YYYY-MM-DD): ")
            end_date = input("Enter end date (YYYY-MM-DD): ")
            plot_data_distribution(start_date, end_date)

        elif choice == '6':
            start_date = input("Enter the start date (YYYY-MM-DD): ")
            end_date = input("Enter the end date (YYYY-MM-DD): ")
            show_db_snapshot(start_date, end_date)
            
        elif choice == '7':
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
