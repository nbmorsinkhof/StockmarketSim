import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle  # better than plt.Rectangle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class LoadData:
    def __init__(self, file):
        self.file_ = file
        self.df_data = pd.DataFrame({})
        self.df_part = pd.DataFrame({})
        self.N_window = 50
        self.window = [3050-self.N_window, 3050] # window [t1, t2]
        self.indicators = []
        self.current_date = ''

    def load_data(self, file_path = ''):
        if file_path == '':
            return
        
        df = pd.read_excel(file_path)
        df = df.iloc[:, 0:5]
        df.columns = ['date', 'open', 'high', 'low', 'close']


        for col in df.columns:
            if col != "date":
                s = df[col].astype(str)
                s = (
                    s.str.replace(";", "", regex=False)
                    .str.replace(",", ".", regex=False)
                )
                df[col] = pd.to_numeric(s, errors="coerce")

        self.df_data = df

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
        ax.plot(x, high, linewidth=2, color='green')
        ax.plot(x, low, linewidth=2, color='red')
        print(len(self.indicators))
        for indicator in self.indicators:
            indicator.plot(ax)

        ax.set_xlabel("Index")
        ax.set_ylabel("Price")
        ax.set_title("Candlestick chart (manual)")
        ax.grid(True)
        ax.set_xlim(-1, len(high) + int(len(high)*xwindowLength/100))
        

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

    


        

