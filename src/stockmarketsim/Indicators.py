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

    def reset_window(self):
        self.upper_band = np.linspace(np.nan,np.nan, self.loader.N_window)
        self.lower_band = np.linspace(np.nan, np.nan, self.loader.N_window)
        self.middle_band = np.linspace(np.nan, np.nan, self.loader.N_window)
        self.update()
        self.plot()

    def update(self):
        idx_end = self.loader.window[-1]
        data = self.loader.df_data["close"].to_numpy(dtype = np.float64)
        for idx in range(self.loader.N_window):
            idx_boll = idx_end-self.loader.N_window+idx

            mean = np.mean(data[idx_boll-self.N_tail: idx_boll])
            std = np.std(data[idx_boll-self.N_tail: idx_boll])

            self.upper_band[idx] = mean + 3*std
            self.lower_band[idx] = mean - 3*std
            self.middle_band[idx] = mean

    def plot(self, ax):
        print(self.middle_band)
        ax.plot(self.middle_band, color='blue')
        ax.plot(self.lower_band, linestyle='--', color='blue')
        ax.plot(self.upper_band, linestyle='--', color='blue')
        
    