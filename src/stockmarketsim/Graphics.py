import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from stockmarketsim.LoadData import LoadData
import stockmarketsim.Indicators as Indicators
from pathlib import Path

class Graphics(tk.Tk):
    def __init__(self, loader: LoadData):
        super().__init__()

        self.title("Candlestick Viewer")
        self.loader = loader
        self.indicators = []
        loader.set_indicators(self.indicators)
        self.is_running = False

        # 1. Create a Figure + Axes for the GUI
        self.fig = Figure(figsize=(10, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)

        
        # 2. Embed the Figure in Tkinter via FigureCanvasTkAgg
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()
        toolbar.pack(side=tk.TOP, fill=tk.X)

        controls_row = tk.Frame(self)
        controls_row.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        left = tk.Frame(controls_row)
        left.pack(side=tk.LEFT, padx=10)
        #LOAD DATA
        self.data_path = tk.StringVar()
        tk.Button(left, text="Load Data", command=self.load_data).grid(row=2, column=0, padx=5, pady=2, sticky='w')
        
     
        tk.Entry(left, textvariable=self.data_path, width=30).grid(row=2, column=1, padx=5, pady=2, sticky="w")
        
        # 3. Button to (re)draw the candles
        button = tk.Button(left, text="Draw candlesticks", command=self.update_plot).grid(row=0, column=0, padx=5, pady=2, sticky="w")
        #button.pack(side=tk.BOTTOM, pady=10)

     
        # 5. add bollinger
        # Row container at the bottom
        button_bollinger = tk.Button(left, text='Bollinger', command=self.add_bollinger).grid(row=1, column=0, padx=5, pady=2, sticky="w")

        # Get bollinger window size
        self.input_bollinger_length = tk.StringVar()
        entry_bollinger_length = tk.Entry(left, textvariable=self.input_bollinger_length, width=15).grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        # Remove bollinger
        tk.Button(left, text='Remove Bollinger', command=self.remove_bollinger).grid(row=1, column=2, padx=5, pady=2, sticky="w")
        
        # Set window length
        self.window_length_x = tk.StringVar()
        tk.Button(left, text='Set horizontal window length', command=self.set_window_length_x).grid(row=3, column=0, pady=2, padx=5, sticky='w')
        tk.Entry(left, textvariable=self.window_length_x).grid(row=3, column=1, pady=2, padx=5, sticky='w')
        
        # Date label

        self.date_label = tk.StringVar(value=f"date at index 0: {loader.current_date}")
        tk.Label(left, textvariable=self.date_label ).grid(row=4, column=0, sticky="w", padx=(0, 8))
        
        #RIGHT
        right = tk.Frame(controls_row)
        right.pack(side=tk.RIGHT, padx=10)
        #Step back
        tk.Button(right, text="Step back", command=self.plot_step_back).pack(side=tk.LEFT, padx=5)
        #STEP
        button_update = tk.Button(right, text="Step next", command=self.plot_step).pack(side=tk.LEFT, padx=5)
        # Run 
        button_run = tk.Button(right, text='Run', command=self.run).pack(side=tk.LEFT, padx=5)

        # Stop
        button_stop = tk.Button(right, text='Stop', command=self.stop_run).pack(side=tk.LEFT, padx=5)


    def update_plot(self):
        # let LoadData draw on our Axes
        self.loader.plot_klines(self.ax)
        self.canvas.draw_idle()
        self.date_label.set(f"date at index {0}: {self.loader.current_date}")

    def plot_step(self):
        self.loader.plot_step()
        for indicator in self.indicators:
            indicator.update()
        self.update_plot()
    
    def plot_step_back(self):
        self.loader.plot_step_back()
        for indicator in self.indicators:
            indicator.update()
        self.update_plot()

    def stop_run(self):
        self.is_running = False

    def run(self):
        self.is_running = True
        self.schedule_next_step()

    def schedule_next_step(self):
        if not self.is_running:
            return
        self.plot_step()
        # call this function again after 50 ms
        self.after(50, self.schedule_next_step)

    def add_bollinger(self):
        print("sting_var:", self.input_bollinger_length.get())
        N = int(self.input_bollinger_length.get())
        
        if N>1:
            self.indicators.append(Indicators.bollinger(LoadData=self.loader, N=N))
        else:
            print("Length not sufficient: ", N)
        print(len(self.indicators))
    
    def remove_bollinger(self):
        self.indicators.pop(-1)
    
    def load_data(self):
        print("loading data")
        data_path = self.data_path.get()
        self.loader.load_data(file_path=Path(data_path))
        
    def set_window_length_x(self):
        N = int(self.window_length_x.get())
        if N>5:
            self.loader.set_window_length_x(N)
        else:
            return
        
