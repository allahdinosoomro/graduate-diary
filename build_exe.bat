@echo off
echo Building Graduate Diary executable with PyInstaller...
pyinstaller --noconfirm --onefile --windowed --add-data "assets;assets" --add-data "database;database" main.py
echo Build finished. Look in the "dist" folder.
pause
