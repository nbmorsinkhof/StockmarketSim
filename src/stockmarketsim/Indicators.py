import numpy as np
from matplotlib import pyplot as plt
class bollinger:
    def __init__(self, LoadData, N, N_std=0):
        self.N_tail=N
        self.N_std = N_std
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
        print("update bollinger")
        idx_end = self.loader.window[-1]
        open = self.loader.df_data["open"].to_numpy(dtype = np.float64)
        low = self.loader.df_data["low"].to_numpy(dtype = np.float64)
        high = self.loader.df_data["high"].to_numpy(dtype = np.float64)
        close = self.loader.df_data["close"].to_numpy(dtype = np.float64)
        data = (open + low + high + close)/4
        for idx in range(self.loader.N_window):
            idx_boll = idx_end-self.loader.N_window+idx
            mean = np.mean(data[idx_boll-self.N_tail: idx_boll])
            std = np.std(data[idx_boll-self.N_tail: idx_boll])

            self.upper_band[idx] = mean + self.N_std*std
            self.lower_band[idx] = mean - self.N_std*std
            self.middle_band[idx] = mean

    def plot(self, ax):
        ax.plot(self.middle_band, color='blue', label='Bollinger', linewidth=0.5)
        ax.plot(self.lower_band, linestyle='--', color='blue', linewidth=0.5)
        ax.plot(self.upper_band, linestyle='--', color='blue', linewidth=0.5)
        ax.fill_between(range(len(self.upper_band)), self.lower_band, self.upper_band, alpha=0.15)
        
class MovingAverage:
    def __init__(self, LoadData, N):
        self.N_tail=N
        self.loader = LoadData
        self.mean = 0
        self.std = 0
        
        self.middle_band = np.linspace(np.nan, np.nan, self.loader.N_window)

    def reset_window(self):
        self.middle_band = np.linspace(np.nan, np.nan, self.loader.N_window)
        self.update()
        self.plot()

    def update(self):
        idx_end = self.loader.window[-1]
        data = self.loader.df_data["close"].to_numpy(dtype = np.float64)
        for idx in range(self.loader.N_window):
            idx_boll = idx_end-self.loader.N_window+idx
            mean = np.mean(data[idx_boll-self.N_tail: idx_boll])

            self.middle_band[idx] = mean

    def plot(self, ax):
        print(self.middle_band)
        ax.plot(self.middle_band, color='orange', linestyle = "--" ,label=("moving average_"+ str(self.N_tail)))

class Polynomial:
    def __init__(self, LoadData):
        self.loader = LoadData
        self.points_x = []
        self.points_y = []
        self.poly_fit = np.linspace(np.nan, np.nan, self.loader.N_window)
        self.poly_fit_x = np.linspace(0, self.loader.N_window-1, self.loader.N_window)
        self.poly_coef = [np.nan, np.nan]
        self.N_first_point = 0
        self.X_first_points = []
        
    def calc_poly(self):
        print("points: ", self.points_x)
        if len(self.points_x)>2:
            print("calc_poly")
            x_points = np.array(self.points_x) -(self.loader.window[0] - self.N_first_point)
            self.poly_coef = np.polyfit(x_points, self.points_y, deg=2)
            print("coefs: ", self.poly_coef)
    
    def add_point(self, x, y):
        if len(self.points_x)<1:
            self.N_first_point = self.loader.window[0]
        self.points_x.append(x+(self.loader.window[0] - self.N_first_point))
        self.points_y.append(y)
        self.calc_poly()
        
    def remove_point(self):
        print("remove poly points")
        self.points_x.pop(-1)
        self.points_y.pop(-1)
        return len(self.points_x)
        
    def update(self):
        print("Update poly")
        self.calc_poly()
        if not np.isnan(self.poly_coef).any():
            a, b, c = self.poly_coef
            x = np.linspace(0, self.loader.total_window_length-1, self.loader.total_window_length)
            self.poly_fit = a * (x)**2 + b * (x) + c
            mask = np.arange(len(self.poly_fit)) >= (self.points_x[0]-(self.loader.window[0] - self.N_first_point))
            self.poly_fit = np.where(mask, self.poly_fit, np.nan)
            
    def plot(self, ax):
        print("plot poly")
        if not np.isnan(self.poly_coef).any():
            a, b, c = self.poly_coef
            x = np.linspace(0, self.loader.total_window_length-1, self.loader.total_window_length)
            self.poly_fit = a * (x)**2 + b * (x) + c
            mask = np.arange(len(self.poly_fit)) >= (self.points_x[0]-(self.loader.window[0] - self.N_first_point))
            self.poly_fit = np.where(mask, self.poly_fit, np.nan)
            print("len poly: ", len(self.poly_fit), " last: ", self.poly_fit[-1], " ", self.loader.total_window_length)
        ax.plot(self.poly_fit)
        ax.scatter(np.array(self.points_x)-(self.loader.window[0] - self.N_first_point), np.array(self.points_y), color="red")
        