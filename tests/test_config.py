"""
Test the configuration management system
"""
import pytest
import os
from unittest.mock import patch, MagicMock
from config.settings import Config

class TestConfig:
    """Test configuration management."""
    
    def test_config_initialization(self):
        """Test that config initializes properly."""
        # Test that Config class exists and has required attributes
        assert hasattr(Config, 'GROQ_API_KEY')
        assert hasattr(Config, 'GEMINI_API_KEY')
        assert hasattr(Config, 'SENDER_EMAIL')
        assert hasattr(Config, 'APP_PASSWORD')
    
    def test_directory_creation(self):
        """Test that ensure_directories creates required directories."""
        Config.ensure_directories()
        
        # Check that directories exist
        assert Config.UPLOAD_FOLDER.exists()
        assert Config.OUTPUT_FOLDER.exists()
        assert Config.TEMP_FOLDER.exists()
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_config_validation(self):
        """Test that validation fails when required config is missing."""
        with pytest.raises(ValueError) as exc_info:
            Config.validate_config()
        
        assert "Missing required configuration" in str(exc_info.value)
    
    @patch.dict(os.environ, {
        'GROQ_API_KEY': 'test_groq_key',
        'GEMINI_API_KEY': 'test_gemini_key',
        'SENDER_EMAIL': 'test@example.com',
        'APP_PASSWORD': 'test_password'
    })
    def test_valid_config_validation(self):
        """Test that validation passes with all required config."""
        # This should not raise an exception
        result = Config.validate_config()
        assert result is True
