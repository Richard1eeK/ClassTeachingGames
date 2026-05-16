@echo off
echo Installing dependencies...
pip install pygame pyinstaller
echo.
echo Building .exe...
pyinstaller --onefile --windowed --name "ShellGame" --add-data "data;data" --add-data "assets;assets" main.py
echo.
echo Done! Find your .exe in the dist/ folder.
pause
