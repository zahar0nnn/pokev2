@echo off
echo 🌐 Pokemon Web App Starter
echo =========================

echo.
echo 🔍 Checking connections...
python check_connection.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Connection test failed!
    echo 💡 Please check the issues above.
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Connection test passed!
echo.
echo 🌐 Starting web application...
echo 💡 Web app will be available at: http://127.0.0.1:5001
echo 💡 Press Ctrl+C to stop the web app
echo.
python app.py

echo.
echo 🎉 Web app stopped!
pause
