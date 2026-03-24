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
        df = self.df_data.iloc[self.window[0]:self.window[1], :].reset_index(drop=True)

        high = df["high"].astype(float).to_numpy()
        low = df["low"].astype(float).to_numpy()
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
        print("updating current_date: ", self.df_data['date'].iloc[self.window[1]], "with index: ",self.window[1])
        self.current_date = str(self.df_data['date'].iloc[self.window[0]])
        self.end_date = str(self.df_data['date'].iloc[self.window[1]])
    
    def set_window_length_x(self, N):
        self.N_window = N
        self.window[1] = self.window[0] + N
    
    def set_date(self, date: str, end_date: str):
        date_str = date + " 00:00:00"
        end_date_str = end_date + " 00:00:00"

        matches_first = np.where(self.df_data.index[self.df_data["date"] == date_str])[0]
        matches_second = self.df_data.index[self.df_data["date"] == end_date_str]
        
        matches_second = np.where(self.df_data["date"] == end_date_str)[0]

        idx_first = matches_first[0] if len(matches_first) > 0 else None
        idx_second = matches_second[0] if len(matches_second) > 0 else None

        print("SETTING DATE:")
        print("  input start:", date)
        print("  input end  :", end_date)
        print("  matches_first :", matches_first)
        print("  matches_second:", matches_second)

        if idx_second is not None:
            print("  row at idx_second:\n", self.df_data.loc[idx_second])

        if idx_first is not None and idx_second is not None:
            self.window[0] = idx_first
            self.window[1] = idx_second

        elif idx_first is None and idx_second is not None:
            print("End date:", self.df_data.loc[idx_second, "date"])
            self.window[0] = idx_second - self.N_window 
            self.window[1] = idx_second 

        elif idx_first is not None and idx_second is None:
            print("Start date:", self.df_data.loc[idx_first, "date"])
            self.window[0] = idx_first
            self.window[1] = idx_first + self.N_window

        else:
            return
            

    


        

