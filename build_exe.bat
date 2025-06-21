@echo off
IF EXIST dist (
    echo Deleting old build...
    rmdir /s /q dist
)

echo Creating portable EXE...
pyinstaller --onefile --windowed --name tournament_creator main.py

IF EXIST dist\tournament_creator.exe (
    echo Done! The file is located in dist\main.exe
) ELSE (
    echo Error! File could not be created.
)

@REM Remove build-folder
rmdir /s /q build

@REM Remove __pycache__ folders
@echo off
set "TARGET=__pycache__"
for /d /r %%D in (*) do (
    if /i "%%~nxD"=="%TARGET%" (
        rd /s /q "%%D"
    )
)

@REM Remove .spec
del .\tournament_creator.spec >nul