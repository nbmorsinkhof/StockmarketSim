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
        self.total_window_length = self.N_window
        self.window = [3050-self.N_window, 3050] # window [t1, t2]
        self.indicators = []
        self.current_date = ''
        self.end_date = ""

    def load_data(self, file_path=''):
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

        df = df.dropna(subset=["open", "high", "low", "close"], how="all")

        self.df_data = df
        print("END:", self.df_data.iloc[-1])

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
        self.total_window_length = len(high) + int(len(high)*xwindowLength/100)
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
        alpha = 0.08
        ax.legend()
        if len(low)<1:
            return
        if len(high)<1:
            return
        min  =np.nanmin(low)
        max = np.nanmax(high)*(1+alpha)
        if min>0 and max>0:
            ax.set_ylim(np.nanmin(low)*(1-alpha), np.nanmax(high)*(1+alpha))
        
        

    def plot_step(self):
        if pd.isna(self.df_data["date"].iloc[self.window[1]+1]):
            return
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
        self.end_date = str(self.df_data['date'].iloc[self.window[1]])
    
    def set_window_length_x(self, N):
        self.N_window = N
        self.window[1] = self.window[0] + N
    
    def set_date(self, date: str, end_date: str):
        date_str = date + " 00:00:00"
        end_date_str = end_date + " 00:00:00"
        matches_first = self.df_data.index[self.df_data["date"] == date_str]
        matches_second = self.df_data.index[self.df_data["date"] == end_date_str]
        idx_first = matches_first[0] if not matches_first.empty else None
        idx_second = matches_second[0] if not matches_second.empty else None
        
        print("SETTING DATE: ",  matches_first, matches_second, self.df_data.iloc[matches_second[0]])
        if idx_first !=None and idx_second!=None:
            self.window[0] = idx_first
            self.window[1] = idx_second
        elif idx_first ==None and idx_second!=None:
            self.window[0] = idx_second - self.N_window
            self.window[1] = idx_second
        elif idx_first !=None and idx_second==None:
            self.window[0] = idx_first
            self.window[1] = idx_first + self.N_window
        else:
            return
            

    


        

