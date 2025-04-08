import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class DataLoader():

    def __init__(self, ticker, start_date, end_date, frequency):
        self.ticker = ticker
        self.start = start_date
        self.end = end_date
        self.frequency = frequency

        assert start_date < end_date, "Start date should be before end date"

    def dataset(self):
        stock_data = yf.download(
            self.ticker,
            start=self.start,
            end=self.end,
            interval=self.frequency,
            progress=False
        )

        # Nettoyage
        stock_data.dropna(inplace=True)  
        stock_data = stock_data[stock_data['Volume'] > 0]  
        stock_data['Return'] = stock_data['Close'].pct_change()
        stock_data.dropna(inplace=True)  

        stock_data = stock_data[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'Return']]
        stock_data.reset_index(inplace=True)

        # Vérification
        if len(stock_data) < 10:
            raise ValueError("Pas assez de données après nettoyage")

        return stock_data

