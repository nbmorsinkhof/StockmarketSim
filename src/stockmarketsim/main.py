#from LoadData import LoadData
from stockmarketsim.LoadData import LoadData
from stockmarketsim.Graphics import Graphics
from pathlib import Path



if __name__ == "__main__":
    path_data = Path(r"C:\Users\NiekMorsinkhof\Documents\data\data.xlsx")

    print(path_data)
    loader = LoadData(path_data)
    loader.load_data()

    app = Graphics(loader)
    app.mainloop()