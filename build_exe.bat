@echo off
echo Deleting old build...
rmdir /s /q dist

echo Creating portable EXE...
pyinstaller --onefile --windowed --name tournament_creator main.py

IF EXIST dist\tournament_creator.exe (
    echo Done! The file is located in dist\main.exe
) ELSE (
    echo Error! File could not be created.
)
