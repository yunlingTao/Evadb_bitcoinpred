import evadb
import psycopg2
import pandas as pd

params = {
    "user": "eva",
    "password": "2021",
    "host": "localhost",
    "port": "5432",
    "database": "postgres_data"
}

# Load the CSV data into a Pandas DataFrame
df = pd.read_csv('content/btc_usd.csv')


# Connect to PostgreSQL
connection = psycopg2.connect(**params)
cursor = connection.cursor()

# Create BTC_USD table if not exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS BTC_USD(
      Currency VARCHAR(64), 
      Date DATE, 
      Closing FLOAT, 
      Open FLOAT, 
      High FLOAT, 
      Low FLOAT
    )
""")

# Insert data from the DataFrame into the BTC_USD table
for index, row in df.iterrows():
    cursor.execute("INSERT INTO BTC_USD (Currency, Date, Closing, Open, High, Low) VALUES (%s, %s, %s, %s, %s, %s)", 
                   (row['Currency'], row['Date'], row['Closing'], row['Open'], row['High'], row['Low']))

connection.commit()
cursor.close()
connection.close()
