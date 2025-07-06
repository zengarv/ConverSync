import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for the meeting assistant application."""
    
    # API Keys
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Model Configuration
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'whisper-large-v3-turbo')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
    
    # Email Configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SENDER_EMAIL = os.getenv('SENDER_EMAIL')
    SENDER_NAME = os.getenv('SENDER_NAME', 'ConverSync')
    APP_PASSWORD = os.getenv('APP_PASSWORD')
    
    # File Paths
    BASE_DIR = Path(__file__).parent.parent
    UPLOAD_FOLDER = BASE_DIR / os.getenv('UPLOAD_FOLDER', 'uploads')
    OUTPUT_FOLDER = BASE_DIR / os.getenv('OUTPUT_FOLDER', 'outputs')
    TEMP_FOLDER = BASE_DIR / os.getenv('TEMP_FOLDER', 'temp')
    
    # PDF Configuration
    COMPANY_NAME = os.getenv('COMPANY_NAME', 'ConverSync AI')
    LOGO_PATH = os.getenv('LOGO_PATH')
    
    # Email Templates
    DEFAULT_EMAIL_SUBJECT = "Minutes of the Meeting"
    DEFAULT_EMAIL_BODY = """
Dear Team,

Attached are the minutes of the recent meeting. Please review and follow up on your respective action items.

Regards,
Meeting Assistant Bot
"""
    
    # Create directories if they don't exist
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist."""
        for folder in [cls.UPLOAD_FOLDER, cls.OUTPUT_FOLDER, cls.TEMP_FOLDER]:
            folder.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present."""
        required_keys = [
            'GROQ_API_KEY',
            'GEMINI_API_KEY',
            'SENDER_EMAIL',
            'APP_PASSWORD'
        ]
        
        missing_keys = []
        for key in required_keys:
            if not getattr(cls, key):
                missing_keys.append(key)
        
        if missing_keys:
            raise ValueError(f"Missing required configuration: {', '.join(missing_keys)}")
        
        return True
