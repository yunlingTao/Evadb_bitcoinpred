from sklearn.metrics import mean_squared_error
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import numpy as np

df = pd.read_csv('content/BTC_USD.csv')
data = df['Closing'].values

train_size = int(len(data) * 0.8)
train, test = data[0:train_size], data[train_size:len(data)]

def evaluate_arima_model(train, test, order):
    history = [x for x in train]
    model = ARIMA(history, order=order)
    model_fit = model.fit()
    predictions = model_fit.forecast(steps=len(test))[0]

    if not isinstance(predictions, (list, tuple, pd.Series, np.ndarray)):
        predictions = [predictions]

    min_len = min(len(test), len(predictions))
    test = test[:min_len]
    predictions = predictions[:min_len]

    mse = mean_squared_error(test, predictions)
    return mse



def arima_grid_search(train, test, p_range, d_range, q_range):
    best_score, best_cfg = float("inf"), None
    for p in p_range:
        for d in d_range:
            for q in q_range:
                order = (p, d, q)
                try:
                    mse = evaluate_arima_model(train, test, order)
                    if mse < best_score:
                        best_score, best_cfg = mse, order
                    print(f"ARIMA{order} MSE={mse:.3f}")
                except Exception as e:
                    print(f"ARIMA{order} encountered an error: {e}")
                    continue
    return best_cfg


p_range = [0, 1, 2, 3, 4, 5]
d_range = [0, 1, 2]
q_range = [0, 1, 2, 3, 4, 5]
best_parameters = arima_grid_search(train, test, p_range, d_range, q_range)
print(f"Best ARIMA parameters: {best_parameters}")
#Best ARIMA parameters: (5, 1, 5)