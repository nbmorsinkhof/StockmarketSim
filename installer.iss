[Setup]
AppName=StockmarketSim
AppVersion=2.1.0
DefaultDirName={autopf}\StockmarketSim
DefaultGroupName=StockmarketSim
OutputDir=.
OutputBaseFilename=StockmarketSim-Setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\StockmarketSim\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\StockmarketSim"; Filename: "{app}\StockmarketSim.exe"
Name: "{commondesktop}\StockmarketSim"; Filename: "{app}\StockmarketSim.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a Desktop icon"; Flags: unchecked

[Run]
Filename: "{app}\StockmarketSim.exe"; Description: "Launch StockmarketSim"; Flags: nowait postinstall skipifsilent
