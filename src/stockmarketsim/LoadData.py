import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle  # better than plt.Rectangle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from kraken.spot import Market as SpotMarket
from binance.client import Client
import time

class LoadData:
    def __init__(self, file):
        self.file_ = file
        self.df_data = pd.DataFrame({})
        self.df_part = pd.DataFrame({})
        self.N_window = 70
        self.window = [0, self.N_window] # window [t1, t2]
        self.indicators = []
        self.current_date = ''
        self.symbol = "XETHZUSD"
        
        self.client = Client()

        

    def load_data(self, file_path = ''):
        klines = self.client.get_historical_klines(
            symbol="ETHUSDT",
            interval=Client.KLINE_INTERVAL_5MINUTE,
            start_str="15 day ago UTC"
        )
        df = pd.DataFrame(klines, columns=[
            "date",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base",
            "taker_buy_quote",
            "ignore"
        ])

        df = df[["date","open","high","low","close","volume"]]

        df["date"] = pd.to_datetime(df["date"], unit="ms")

        df[["open","high","low","close","volume"]] = df[
            ["open","high","low","close","volume"]
        ].astype(float)
        

        self.df_data = df
        high = np.array(df["high"]).astype(float)[self.window[0]: self.window[1]]
        low = np.array(df["low"]).astype(float)[self.window[0]: self.window[1]]
        open = np.array(df["open"]).astype(float)[self.window[0]: self.window[1]]
        close = np.array(df["close"]).astype(float)[self.window[0]: self.window[1]]
        self.y_data = (high+low+open+close)/4
        return

    def plot_klines(self, ax, xwindowLength: int):
        """
        Draw candlesticks on the given Matplotlib Axes (ax).
        Does NOT create its own Figure or call plt.show().
        """
        df = self.df_data

        # pick a slice
        df.iloc[self.window[0]: self.window[1], :].reset_index(drop=True)
        
        high = np.array(df["high"]).astype(float)[self.window[0]: self.window[1]]
        low = np.array(df["low"]).astype(float)[self.window[0]: self.window[1]]
        open = np.array(df["open"]).astype(float)[self.window[0]: self.window[1]]
        close = np.array(df["close"]).astype(float)[self.window[0]: self.window[1]]
        self.y_data = (high+low+open+close)/4

        x = np.arange(len(high))  # x indices from 0 to len(df_part)-1
        self.x_data = x
        ax.clear()  # clear previous contents

        #indicators
        ax.plot(x, high, linewidth=1, color='green')
        ax.plot(x, low, linewidth=1, color='red')
        print(len(self.indicators))
        for indicator in self.indicators:
            indicator["object"].plot(ax)

        ax.set_xlabel("Index")
        ax.set_ylabel("Price")
        ax.set_title("Candlestick chart (manual)")
        ax.grid(True)
        ax.set_xlim(-1, len(high) + int(len(high)*xwindowLength/100))
        ax.legend()
        

    def plot_step(self):
        self.window[0]+=1
        self.window[1]+=1
    
    def plot_step_back(self):
        self.window[0]-=1
        self.window[1]-=1

    def set_indicators(self, indicators):
        self.indicators = indicators
    
    def set_window_length_x(self, N):
        self.N_window = N
        self.window[1] = self.window[0] + N
        x = np.arange(self.N_window)  # x indices from 0 to len(df_part)-1
        self.x_data = x
        high = np.array(self.df_data["high"]).astype(float)[self.window[0]: self.window[1]]
        low = np.array(self.df_data["low"]).astype(float)[self.window[0]: self.window[1]]
        open = np.array(self.df_data["open"]).astype(float)[self.window[0]: self.window[1]]
        close = np.array(self.df_data["close"]).astype(float)[self.window[0]: self.window[1]]
        self.y_data = (high+low+open+close)/4
    
    def set_date(self, date: str):
        date_str = date + " 00:00:00"
        matches = self.df_data.index[self.df_data["date"] == date_str]
        idx = matches[0] if not matches.empty else None
        if idx !=None:
            self.window[0] = idx
            self.window[1] = idx + self.N_window

    


        

