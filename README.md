# Soltech_Python_HistorianTag
솔텍시스템-히스토리안 태그 조회 프로그램, Python

pip install pandas
pip install PyQt6
pip install PyQt5designer
pip install pythonnet

pyinstaller --onefile --noconsole --add-data "dll/IHUAPI.dll;dll" --add-data "dll/IHUAPI_32.dll;dll" --add-data "dll/Utilities.dll;dll" --add-data "dll/Utilities_32.dll;dll" --add-data "dll/Proficy.Historian.ClientAccess.API.dll;dll" --add-data="icon.ico;." --icon="icon.ico" --name HistorianTag main.py
