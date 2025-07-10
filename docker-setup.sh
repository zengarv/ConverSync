#!/bin/bash

# ConverSync Docker Setup Script
# This script helps you get started with ConverSync using Docker

set -e

echo "🚀 ConverSync Docker Setup"
echo "=========================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Docker installation
if ! command_exists docker; then
    echo "❌ Docker is not installed. Please install Docker Desktop and try again."
    echo "   Download from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check Docker Compose installation
if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

echo "✅ Docker and Docker Compose found"

# Check if .env file exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📝 Creating .env file from .env.example..."
        cp .env.example .env
        echo "⚠️  Please edit .env file and add your API keys before running the application"
        echo "   Required keys: GROQ_API_KEY, GEMINI_API_KEY"
    else
        echo "❌ .env.example file not found. Please create a .env file with your configuration."
        exit 1
    fi
else
    echo "✅ .env file found"
fi

# Create necessary directories
echo "📁 Creating required directories..."
mkdir -p uploads outputs temp

echo ""
echo "🐳 Docker setup options:"
echo "1. Production build (recommended for first-time setup)"
echo "2. Development mode (with hot reload)"
echo "3. Production with Nginx reverse proxy"
echo "4. Frontend development only"
echo ""

read -p "Choose an option (1-4): " choice

case $choice in
    1)
        echo "🏗️  Building and starting ConverSync in production mode..."
        docker-compose up --build
        ;;
    2)
        echo "🏗️  Building and starting ConverSync in development mode..."
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
        ;;
    3)
        echo "🏗️  Building and starting ConverSync with Nginx..."
        docker-compose --profile production up --build
        ;;
    4)
        echo "🏗️  Starting frontend development server..."
        docker-compose --profile frontend-dev up --build frontend-dev
        ;;
    *)
        echo "❌ Invalid option. Please run the script again and choose 1-4."
        exit 1
        ;;
esac

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Access your application:"
case $choice in
    1|2)
        echo "   🌐 Application: http://localhost:5000"
        ;;
    3)
        echo "   🌐 Application: http://localhost (port 80)"
        echo "   🔧 Direct access: http://localhost:5000"
        ;;
    4)
        echo "   🌐 Frontend: http://localhost:3000"
        echo "   ⚠️  Backend needs to be started separately"
        ;;
esac

echo ""
echo "📚 Useful commands:"
echo "   docker-compose logs -f          # View logs"
echo "   docker-compose down             # Stop services"
echo "   docker-compose restart          # Restart services"
echo "   docker-compose exec conversync bash  # Access container shell"
echo ""
echo "📖 For more details, see DOCKER.md"
