import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from stockmarketsim.LoadData import LoadData
import stockmarketsim.Indicators as Indicators
from pathlib import Path
import time

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
        
        # ScrollBar
        controls_row = tk.Frame(self)
        controls_row.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # Canvas is the scrollable viewport
        controls_canvas = tk.Canvas(controls_row, highlightthickness=0, height=140)  # choose a height
        controls_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar controls the canvas
        vscroll = tk.Scrollbar(controls_row, orient="vertical", command=controls_canvas.yview)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        controls_canvas.configure(yscrollcommand=vscroll.set)

        # LEft frame
        #left = tk.Frame(controls_row)
        #left.pack(side=tk.LEFT, padx=10)
        left = tk.Frame(controls_canvas)
        win_id = controls_canvas.create_window((0, 0), window=left, anchor="nw")
        
        def _on_frame_configure(event=None):
            controls_canvas.configure(scrollregion=controls_canvas.bbox("all"))

        left.bind("<Configure>", _on_frame_configure)

        def _on_canvas_configure(event):
            controls_canvas.itemconfigure(win_id, width=event.width)

        controls_canvas.bind("<Configure>", _on_canvas_configure)
        def _on_mousewheel(event):
            # Windows/macOS
            controls_canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")

        controls_canvas.bind_all("<MouseWheel>", _on_mousewheel)      # Windows/macOS
        #LOAD DATA
        self.data_path = tk.StringVar()
        tk.Button(left, text="Load Data", command=self.browse_files).grid(row=2, column=0, padx=5, pady=2, sticky='w')
        
        # 3. Button to (re)draw the candles
        button = tk.Button(left, text="Update Plot", command=self.update_plot).grid(row=0, column=0, padx=5, pady=2, sticky="w")
        #button.pack(side=tk.BOTTOM, pady=10)

        # 5. add bollinger
        # Row container at the bottom
        button_bollinger = tk.Button(left, text='Bollinger', command=self.add_bollinger).grid(row=1, column=0, padx=5, pady=2, sticky="w")

        # Get bollinger window size
        self.input_bollinger_length = tk.StringVar()
        entry_bollinger_length = tk.Entry(left, textvariable=self.input_bollinger_length, width=5).grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        self.input_bollinger_std = tk.StringVar()
        entry_bollinger_std = tk.Entry(left, textvariable=self.input_bollinger_std, width=5).grid(row=1, column=1, padx=5, pady=2, sticky="e")
        # Remove bollinger
        tk.Button(left, text='Remove Bollinger', command=self.remove_bollinger).grid(row=1, column=2, padx=5, pady=2, sticky="w")
        
        # Set window length
        self.window_length_x = tk.StringVar()
        tk.Button(left, text='Set horizontal window length', command=self.set_window_length_x).grid(row=3, column=0, pady=2, padx=5, sticky='w')
        tk.Entry(left, textvariable=self.window_length_x).grid(row=3, column=1, pady=2, padx=5, sticky='w')
        self.xwindowLength = tk.IntVar()
        tk.Scale(left, variable = self.xwindowLength, from_=0, to_=100, orient="horizontal").grid(row=3, column=2, pady=2, padx=5, sticky='w')

        # Set Date
        self.first_date = tk.StringVar()
        tk.Button(left, text='Set Date', command=self.set_first_date).grid(row=5, column=0, pady=2, padx=5, sticky='w')
        tk.Entry(left, textvariable=self.first_date).grid(row=5, column=1, pady=2, padx=5, sticky='w')
        
        # Date label

        self.date_label = tk.StringVar(value=f"date at index 0: {loader.current_date}")
        tk.Label(left, textvariable=self.date_label ).grid(row=4, column=0, sticky="w", padx=(0, 8))
        
        #RIGHT
        right = tk.Frame(controls_row)
        right.pack(side=tk.RIGHT, padx=10)
        #Step back
        tk.Button(right, text="Step back", command=self.plot_step_back).grid(row=0, column=0, pady=2, padx=5, sticky='w')#rid(side=tk.LEFT, padx=5)
        #STEP
        button_update = tk.Button(right, text="Step next", command=self.plot_step).grid(row=0, column=1, pady=2, padx=5, sticky='w')#pack(side=tk.LEFT, padx=5)
        # Run 
        button_run = tk.Button(right, text="Run/Stop", command=self.run).grid(row=0, column=2, pady=2, padx=5, sticky='w')#pack(side=tk.LEFT, padx=5)


        self.speed = tk.IntVar()
        tk.Scale(right, variable = self.speed, from_=0, to_=100, orient="horizontal", length=140).grid(row=1, column=0, pady=2, padx=5, sticky='w')


    def update_plot(self):
        # let LoadData draw on our Axes
        self.loader.plot_klines(self.ax, self.xwindowLength.get())
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

    def run(self):
        self.is_running = not self.is_running
        self.schedule_next_step()

    def schedule_next_step(self):
        if not self.is_running:
            return
        

        v = ((self.speed.get()) / 100.0) * 1.0 
        
        if v>0:
            tick = int(60/v)

        if self.speed.get()>0:
            self.plot_step()
            self.after(tick, self.schedule_next_step)
        else:
            self.after(100, self.schedule_next_step)
            
        

    def add_bollinger(self):
        print("sting_var:", self.input_bollinger_length.get())
        N = int(self.input_bollinger_length.get())
        N_std = float(self.input_bollinger_std.get())
        
        if N>1 and N_std>0:
            self.indicators.append(Indicators.bollinger(LoadData=self.loader, N=N, N_std=N_std))
            self.update_plot()
        else:
            print("Length not sufficient: ", N)
        print(len(self.indicators))
    
    def remove_bollinger(self):
        self.indicators.pop(-1)
        self.update_plot()
    
    def load_data(self):
        print("loading data")
        data_path = self.data_path.get()
        self.loader.load_data(file_path=Path(data_path))
        self.update_plot()
        
    def set_window_length_x(self):
        N = int(self.window_length_x.get())
        if N>5:
            self.loader.set_window_length_x(N)
            for indicator in self.indicators:
                indicator.reset_window()
                
            self.update_plot()
        else:
            return
        
        
    def browse_files(self):
        filename = tk.filedialog.askopenfilename(
            initialdir="/",
            title = "Select a File",
            filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*")),
        )
        self.loader.load_data(file_path=Path(filename))
        
    def set_first_date(self):
        date = self.first_date.get()
        self.loader.set_date(date=date)
        self.update_plot()