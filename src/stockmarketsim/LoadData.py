import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle  # better than plt.Rectangle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from kraken.spot import Market as SpotMarket
import time

class LoadData:
    def __init__(self, file):
        self.file_ = file
        self.df_data = pd.DataFrame({})
        self.df_part = pd.DataFrame({})
        self.N_window = 50
        self.window = [3050-self.N_window, 3050] # window [t1, t2]
        self.indicators = []
        self.current_date = ''
        self.symbol = "XETHZUSD"

    def load_data(self, file_path = ''):
        now_s = int(time.time())
        symbol = self.symbol
        self.last_update_time = now_s
        try:
            resp = SpotMarket().get_ohlc(
                tick_type="trade",
                symbol=symbol,
                resolution="5m",
                from_=now_s-100000,
                to=now_s,
            )
        except Exception as e:
            print("Fetching ohlc futures failed: ", e)
        # Response looks like: {"candles": [{"time": 1680624000000, "open": "...", ...}], "more_candles": True/False}
        candles = resp.get("candles", [])

        df = pd.DataFrame(candles)
        if df.empty:
            self.df_data = df
            return

        # To float type
        df["time"] = pd.to_datetime(df["time"].astype(int), unit="ms", utc=True)
        for c in ["open", "high", "low", "close", "volume"]:
            df[c] = df[c].astype(float)

        self.df_data = df[["time", "open", "high", "low", "close", "volume"]]

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

        x = np.arange(len(high))  # x indices from 0 to len(df_part)-1

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
        self.update_current_date()
    
    def plot_step_back(self):
        self.window[0]-=1
        self.window[1]-=1

    def set_indicators(self, indicators):
        self.indicators = indicators
        
    def update_current_date(self):
        self.current_date = str(self.df_data['date'].iloc[self.window[0]])
    
    def set_window_length_x(self, N):
        self.N_window = N
        self.window[1] = self.window[0] + N
    
    def set_date(self, date: str):
        date_str = date + " 00:00:00"
        matches = self.df_data.index[self.df_data["date"] == date_str]
        idx = matches[0] if not matches.empty else None
        if idx !=None:
            self.window[0] = idx
            self.window[1] = idx + self.N_window

    


        

