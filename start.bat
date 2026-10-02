@echo off
chcp 65001 >nul
setlocal
set PORT=3000
cd /d "%~dp0"
echo ========================================
echo   总工作台 All-in-One Console
echo   http://127.0.0.1:%PORT%/
echo   (也可直接双击 index.html，file:// 直开)
echo ========================================
python "%~dp0serve.py" --port %PORT%
endlocal
