# CS4420_Pj1

## Introduction
This is a bitcoin value forecasting project that will predict future bitcoin value based on historical data.

## Quick Start
First clone this project
```
git@github.com:yunlingTao/Evadb_bitcoinpred.git
cd Evadb_bitcoinpred
```
Install requirements

```
pip install -r requirements.txt
```

Then run 
```
python stocks_exchange.py
```


## Output
There are six options:
1. Get stock data for a specific date - query would find the row of data for the specific date that the user provided

<img width="565" alt="Screen Shot 2023-11-25 at 11 44 10 PM" src="https://github.com/yunlingTao/Evadb_bitcoinpred/assets/113263652/c209bb24-2809-49c5-a0cb-3e84e58f347f">

2. Modify stock data - query would scrape the stocks exchange data for bitcoin from yahoo finance (from 14 days before the start date to the end date) and insert them into the database if the date does not yet have values. Then a snapshot of the table of those dates would be shown.

<img width="402" alt="Screen Shot 2023-11-25 at 11 45 33 PM" src="https://github.com/yunlingTao/Evadb_bitcoinpred/assets/113263652/0d2bef9d-70f3-446c-938a-f297a86f87af">


3. Prediction future stock price - A random forest model that predict future stock price based on previous data 
<img width="255" alt="Screen Shot 2023-11-25 at 11 46 55 PM" src="https://github.com/yunlingTao/Evadb_bitcoinpred/assets/113263652/5df33e95-0bbc-4df4-a6a2-bed8bbc43727">

  
4. Summarize stock data - provide a summary of stock data for a user-given range of time. This functionality cultivates the power of OpenAI where the “gpt-3.5-turbo” model is used to provide a short analysis of the trend of the data exchange data within the date range specified by the user.

<img width="548" alt="Screen Shot 2023-11-25 at 11 47 35 PM" src="https://github.com/yunlingTao/Evadb_bitcoinpred/assets/113263652/65fa61fb-a6c5-4fc5-9f56-0dfd4427ebbe">

5.Show data distribution plot - show the data distribution of each column of stock exchange data (closing price, open price, low price, and high price) within a given date range


<img width="682" alt="Screen Shot 2023-11-25 at 11 47 57 PM" src="https://github.com/yunlingTao/Evadb_bitcoinpred/assets/113263652/7838c3fe-b297-4500-85eb-5c3b6d715b90">

6.Show database snapshot - user is expected to give a date range and the stock exchange data of this date range would be shown

<img width="377" alt="Screen Shot 2023-11-25 at 11 48 12 PM" src="https://github.com/yunlingTao/Evadb_bitcoinpred/assets/113263652/165d8894-a4a9-4af4-9c65-00292b4296b9">


