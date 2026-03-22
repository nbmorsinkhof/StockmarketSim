import numpy as np
from matplotlib import pyplot as plt
from dataclasses import dataclass, field
import copy
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
        idx_end = self.loader.window[-1]
        data = self.loader.df_data["close"].to_numpy(dtype = np.float64)
        for idx in range(self.loader.N_window):
            idx_boll = idx_end-self.loader.N_window+idx
            mean = np.mean(data[idx_boll-self.N_tail: idx_boll])
            std = np.std(data[idx_boll-self.N_tail: idx_boll])

            self.upper_band[idx] = mean + self.N_std*std
            self.lower_band[idx] = mean - self.N_std*std
            self.middle_band[idx] = mean

    def plot(self, ax):
        print(self.middle_band)
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



@dataclass
class Tops:
    tops: list = field(default_factory=list)
    idcs: list = field(default_factory=list)
    detection_idcs: list = field(default_factory=list)
class TopFractal:
    def __init__(self, LoadData, N_layers=1):
        self.N_layers = N_layers
        self.loader = LoadData
        self.tops = []
        self.last_topthrough = [np.nan]
        self.last_index = self.loader.window[1]
        
        
    def first_bottom_detection(self):
        bottom = Tops()
        signal_idcs = self.loader.x_data
        signal = np.array(self.loader.df_data["low"])[self.loader.window[0]: self.loader.window[1]]
        self.poly = []

        for idx in range(1, len(signal)-1):
            if idx>=len(signal):
                break
            if signal[idx-1]>signal[idx] and signal[idx]<signal[idx+1]:
                bottom.tops.append(signal[idx])
                bottom.idcs.append(signal_idcs[idx])
                bottom.detection_idcs.append(signal_idcs[idx+1])
        return copy.copy(bottom) 

    def first_top_detection(self):
        tops = Tops()
        signal_idcs = self.loader.x_data
        signal = np.array(self.loader.df_data["high"])[self.loader.window[0]: self.loader.window[1]]
        self.poly = []

        for idx in range(1, len(signal)-1):
            if idx>=len(signal):
                break
            if signal[idx-1]<signal[idx] and signal[idx]>signal[idx+1]:
                tops.tops.append(signal[idx])
                tops.idcs.append(signal_idcs[idx])
                tops.detection_idcs.append(signal_idcs[idx+1])
        return copy.copy(tops)
    
    def next_layer_tops(self, tops_prev):
        next_tops = Tops()
        for idx in range(1, len(tops_prev.tops)-1):
            if tops_prev.tops[idx-1]<tops_prev.tops[idx] and tops_prev.tops[idx]>tops_prev.tops[idx+1]:
                next_tops.tops.append(copy.copy(tops_prev.tops[idx]))
                next_tops.idcs.append(copy.copy(tops_prev.idcs[idx]))
                next_tops.detection_idcs.append(copy.copy(tops_prev.detection_idcs[idx+1]))
        return copy.copy(next_tops)
    def step_back(self):
        print( "step_back fractal")
        self.last_topthrough.pop(-1)
        self.last_topthrough.pop(-1)

    def update(self):
        self.tops = []
        self.bottoms = []
        for layer_idx in range(self.N_layers):
            if layer_idx==0:
                self.tops.append(self.first_top_detection())
            else:
                self.tops.append(self.next_layer_tops(self.tops[-1]))
                
                
        if self.last_index<self.loader.window[1]:
            if len(self.tops[0].idcs)>1:
                if self.tops[0].tops[-2]>self.tops[0].tops[-1]:
                    self.last_topthrough.append(self.tops[0].tops[-1])
                else:
                    self.last_topthrough.append(self.last_topthrough[-1])
            else:     
                self.last_topthrough.append(self.last_topthrough[-1])        
            
            for layer_idx in range(self.N_layers):
                if layer_idx==0:
                    self.bottoms.append(self.first_bottom_detection())
                # else:
                #     self.tops.append(self.next_layer_tops(self.tops[-1]))
        
        self.last_index = self.loader.window[1]
        
        fit_data = self.loader.y_data[self.tops[-1].idcs[-1]: self.loader.x_data[-1]]
        self.poly_x = self.loader.x_data[-len(fit_data): ]
        print("IDX: ", self.tops[-1].idcs[-1])
        a, b, c = np.polyfit(x=self.poly_x, y=fit_data, deg=2)
        self.poly_y = a*self.poly_x**2 + b*self.poly_x + c

    def plot(self, ax):
        for top in self.tops:
            ax.plot(top.idcs, top.tops, linewidth=2.5)
            
            ax.plot(self.poly_x, self.poly_y, color="red")
        for bottom in self.bottoms:
            ax.plot(bottom.idcs, bottom.tops, linewidth=2.5)
            
        while len(self.last_topthrough)>len(self.loader.x_data):
            self.last_topthrough.pop(0)
            print("pop last trough")
            
        ax.plot(self.loader.x_data[-len(self.last_topthrough):], self.last_topthrough, color="purple")
        
    