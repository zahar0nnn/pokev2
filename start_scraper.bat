@echo off
echo 🔧 Pokemon Scraper & Web App Startup Script
echo ============================================

echo.
echo 🔍 Testing connections...
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
echo 🚀 Starting Pokemon scraper...
python scraper.py

echo.
echo 🌐 Starting web application...
echo 💡 Web app will be available at: http://127.0.0.1:5001
echo 💡 Press Ctrl+C to stop the web app
echo.
python app.py

echo.
echo 🎉 All done!
pause
