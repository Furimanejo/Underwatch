rmdir /s /q .\dist
pyinstaller --clean --onefile underwatch.pyw
xcopy .\templates .\dist\templates\
pause