#!/bin/bash

# ConverSync Development Setup Script

echo "🚀 Setting up ConverSync Development Environment..."

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ and try again."
    exit 1
fi

echo "✅ Python and Node.js found"

# Setup Python backend
echo "📦 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Python dependencies installed"
else
    echo "❌ requirements.txt not found"
    exit 1
fi

# Setup React frontend
echo "📦 Installing Node.js dependencies..."
cd frontend
if [ -f "package.json" ]; then
    npm install
    echo "✅ Node.js dependencies installed"
else
    echo "❌ package.json not found in frontend directory"
    exit 1
fi

# Build frontend for production
echo "🏗️ Building React frontend..."
npm run build
echo "✅ Frontend built successfully"

cd ..

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️ .env file not found. Please copy .env.example to .env and configure your API keys."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "📝 Created .env file from .env.example template"
    fi
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Configure your API keys in the .env file:"
echo "   - GROQ_API_KEY"
echo "   - GEMINI_API_KEY"
echo "   - Email settings (SMTP_SERVER, etc.)"
echo ""
echo "2. Start the development server:"
echo "   python api/flask_app.py"
echo ""
echo "3. For frontend development with hot reload:"
echo "   cd frontend && npm run dev"
echo ""
echo "4. Access the application:"
echo "   - Production build: http://localhost:5000"
echo "   - Development mode: http://localhost:3000 (if running npm run dev)"
echo ""
