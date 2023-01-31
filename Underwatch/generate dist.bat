rmdir /s /q .\dist
pyinstaller --clean --onefile underwatch.py
xcopy .\templates .\dist\templates\
pause