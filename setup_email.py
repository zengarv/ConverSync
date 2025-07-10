#!/usr/bin/env python3
"""
Setup script to configure email settings for ConverSync.
"""

import os
from pathlib import Path

def create_env_file():
    """Create .env file with email configuration."""
    print("📧 ConverSync Email Configuration Setup")
    print("=" * 50)
    
    env_path = Path('.env')
    env_example_path = Path('.env.example')
    
    # Check if .env already exists
    if env_path.exists():
        print("⚠️  .env file already exists.")
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            print("Setup cancelled.")
            return False
    
    # Read the example file as template
    if env_example_path.exists():
        with open(env_example_path, 'r') as f:
            template = f.read()
    else:
        template = """# API Keys
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_NAME=ConverSync
APP_PASSWORD=your_app_password_here

# Model Configuration
GROQ_MODEL=whisper-large-v3-turbo
GEMINI_MODEL=gemini-2.5-flash

# File Paths
UPLOAD_FOLDER=uploads
OUTPUT_FOLDER=outputs
TEMP_FOLDER=temp

# PDF Configuration
COMPANY_NAME=Your Company Name
LOGO_PATH=assets/logo.png
"""
    
    print("\n📝 Please provide your email configuration:")
    print("💡 For Gmail, you'll need to:")
    print("   1. Enable 2-factor authentication")
    print("   2. Generate an App Password")
    print("   3. Use the App Password (not your regular password)")
    print()
    
    # Get user input
    sender_email = input("📧 Your Gmail address: ").strip()
    if not sender_email:
        print("❌ Email address is required.")
        return False
    
    app_password = input("🔐 Your Gmail App Password: ").strip()
    if not app_password:
        print("❌ App password is required.")
        return False
    
    sender_name = input("👤 Sender name (default: ConverSync): ").strip() or "ConverSync"
    company_name = input("🏢 Company name (default: ConverSync AI): ").strip() or "ConverSync AI"
    
    # API Keys (optional for email testing)
    print("\n🔑 API Keys (optional - you can add these later):")
    groq_key = input("🤖 GROQ API Key (leave empty to skip): ").strip() or "your_groq_api_key_here"
    gemini_key = input("🧠 Gemini API Key (leave empty to skip): ").strip() or "your_gemini_api_key_here"
    
    # Update template with user values
    env_content = template.replace("your_email@gmail.com", sender_email)
    env_content = env_content.replace("your_app_password_here", app_password)
    env_content = env_content.replace("ConverSync", sender_name)
    env_content = env_content.replace("Your Company Name", company_name)
    env_content = env_content.replace("your_groq_api_key_here", groq_key)
    env_content = env_content.replace("your_gemini_api_key_here", gemini_key)
    
    # Write .env file
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"\n✅ Configuration saved to {env_path}")
    print("\n📋 Email settings configured:")
    print(f"   📧 Email: {sender_email}")
    print(f"   👤 Name: {sender_name}")
    print(f"   🏢 Company: {company_name}")
    
    return True

def test_email_config():
    """Test the email configuration."""
    print("\n🧪 Testing email configuration...")
    
    try:
        import requests
        
        # Test the health endpoint first
        response = requests.get("http://localhost:5000/health")
        if response.status_code != 200:
            print("❌ Server is not running. Please start the Flask server first:")
            print("   python api/flask_app.py")
            return False
        
        # Test email configuration
        response = requests.post("http://localhost:5000/debug/test-email", 
                               json={"recipients": ["test@example.com"]})
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Email configuration test passed!")
                return True
            else:
                print(f"❌ Email test failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Email test request failed: {response.status_code}")
            return False
            
    except requests.ConnectionError:
        print("❌ Could not connect to server. Please start the Flask server first:")
        print("   python api/flask_app.py")
        return False
    except ImportError:
        print("❌ requests library not installed. Please install requirements:")
        print("   pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ConverSync Email Setup")
    print("=" * 50)
    
    # Create .env file
    if create_env_file():
        print("\n💡 Next steps:")
        print("1. Start the Flask server: python api/flask_app.py")
        print("2. Test email functionality: python test_email_functionality.py")
        print("3. Open http://localhost:5000 to use the application")
        
        # Offer to test if server is running
        test_now = input("\n🧪 Test email configuration now? (y/N): ").strip().lower()
        if test_now == 'y':
            test_email_config()
    
    print("\n🎉 Setup complete!")
