@echo off
echo 🚀 Setting up ConverSync Development Environment...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 16+ and try again.
    pause
    exit /b 1
)

echo ✅ Python and Node.js found

REM Setup Python backend
echo 📦 Installing Python dependencies...
if exist requirements.txt (
    pip install -r requirements.txt
    echo ✅ Python dependencies installed
) else (
    echo ❌ requirements.txt not found
    pause
    exit /b 1
)

REM Setup React frontend
echo 📦 Installing Node.js dependencies...
cd frontend
if exist package.json (
    call npm install
    echo ✅ Node.js dependencies installed
) else (
    echo ❌ package.json not found in frontend directory
    pause
    exit /b 1
)

REM Build frontend for production
echo 🏗️ Building React frontend...
call npm run build
echo ✅ Frontend built successfully

cd ..

REM Check if .env file exists
if not exist .env (
    echo ⚠️ .env file not found. Please copy .env.example to .env and configure your API keys.
    if exist .env.example (
        copy .env.example .env
        echo 📝 Created .env file from .env.example template
    )
)

echo.
echo 🎉 Setup complete!
echo.
echo 📋 Next steps:
echo 1. Configure your API keys in the .env file:
echo    - GROQ_API_KEY
echo    - GEMINI_API_KEY
echo    - Email settings (SMTP_SERVER, etc.)
echo.
echo 2. Start the development server:
echo    python api/flask_app.py
echo.
echo 3. For frontend development with hot reload:
echo    cd frontend ^&^& npm run dev
echo.
echo 4. Access the application:
echo    - Production build: http://localhost:5000
echo    - Development mode: http://localhost:3000 (if running npm run dev)
echo.
pause
