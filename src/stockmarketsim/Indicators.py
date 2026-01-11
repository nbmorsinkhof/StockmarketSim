import numpy as np
from matplotlib import pyplot as plt


class bollinger:
    def __init__(self, LoadData, N):
        self.N_tail=N
        self.loader = LoadData
        self.mean = 0
        self.std = 0

        self.upper_band = np.linspace(np.nan,np.nan, self.loader.N_window)
        self.lower_band = np.linspace(np.nan, np.nan, self.loader.N_window)
        self.middle_band = np.linspace(np.nan, np.nan, self.loader.N_window)

    def update(self):
        idx_end = self.loader.window[-1]
        for idx in range(self.loader.N_window):
            idx_boll = idx_end-self.loader.N_window+idx
            print(idx_boll)
            mean = (self.loader.df_data["close"].iloc[idx_boll-self.N_tail: idx_boll]).mean()
            std = (self.loader.df_data["close"].iloc[idx_boll-self.N_tail: idx_boll]).std()
            print(mean, type(mean))
            self.upper_band[idx] = mean + 3*std
            self.lower_band[idx] = mean - 3*std
            self.middle_band[idx] = mean

    def plot(self, ax):
        print(self.middle_band)
        ax.plot(self.middle_band, color='red')
        ax.plot(self.lower_band, linestyle='--', color='red')
        ax.plot(self.upper_band, linestyle='--', color='red')
        
    