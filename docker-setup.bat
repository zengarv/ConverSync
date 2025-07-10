@echo off
REM ConverSync Docker Setup Script for Windows
REM This script helps you get started with ConverSync using Docker

echo 🚀 ConverSync Docker Setup
echo ==========================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop and try again.
    echo    Download from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    docker compose version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Docker Compose is not installed. Please install Docker Compose and try again.
        pause
        exit /b 1
    )
)

echo ✅ Docker and Docker Compose found

REM Check if .env file exists
if not exist .env (
    if exist .env.example (
        echo 📝 Creating .env file from .env.example...
        copy .env.example .env
        echo ⚠️  Please edit .env file and add your API keys before running the application
        echo    Required keys: GROQ_API_KEY, GEMINI_API_KEY
    ) else (
        echo ❌ .env.example file not found. Please create a .env file with your configuration.
        pause
        exit /b 1
    )
) else (
    echo ✅ .env file found
)

REM Create necessary directories
echo 📁 Creating required directories...
if not exist uploads mkdir uploads
if not exist outputs mkdir outputs
if not exist temp mkdir temp

echo.
echo 🐳 Docker setup options:
echo 1. Production build (recommended for first-time setup)
echo 2. Development mode (with hot reload)
echo 3. Production with Nginx reverse proxy
echo 4. Frontend development only
echo.

set /p choice="Choose an option (1-4): "

if "%choice%"=="1" (
    echo 🏗️  Building and starting ConverSync in production mode...
    docker-compose up --build
) else if "%choice%"=="2" (
    echo 🏗️  Building and starting ConverSync in development mode...
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
) else if "%choice%"=="3" (
    echo 🏗️  Building and starting ConverSync with Nginx...
    docker-compose --profile production up --build
) else if "%choice%"=="4" (
    echo 🏗️  Starting frontend development server...
    docker-compose --profile frontend-dev up --build frontend-dev
) else (
    echo ❌ Invalid option. Please run the script again and choose 1-4.
    pause
    exit /b 1
)

echo.
echo 🎉 Setup complete!
echo.
echo 📋 Access your application:
if "%choice%"=="1" (
    echo    🌐 Application: http://localhost:5000
) else if "%choice%"=="2" (
    echo    🌐 Application: http://localhost:5000
) else if "%choice%"=="3" (
    echo    🌐 Application: http://localhost (port 80)
    echo    🔧 Direct access: http://localhost:5000
) else if "%choice%"=="4" (
    echo    🌐 Frontend: http://localhost:3000
    echo    ⚠️  Backend needs to be started separately
)

echo.
echo 📚 Useful commands:
echo    docker-compose logs -f          # View logs
echo    docker-compose down             # Stop services
echo    docker-compose restart          # Restart services
echo    docker-compose exec conversync bash  # Access container shell
echo.
echo 📖 For more details, see DOCKER.md
pause
