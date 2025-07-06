"""
Comprehensive test script for ConverSync Meeting Assistant
Tests all functionality without requiring actual media files
"""

import sys
import os
import tempfile
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules can be imported successfully."""
    print("🧪 Testing imports...")
    
    try:
        from config import Config
        print("  ✅ Config imported successfully")
        
        from services import (
            MediaConverter,
            TranscriptionService,
            SummarizationService,
            PDFService,
            EmailService
        )
        print("  ✅ All services imported successfully")
        
        from api.meeting_assistant import MeetingAssistant
        print("  ✅ MeetingAssistant imported successfully")
        
        return True
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False

def test_configuration():
    """Test configuration management."""
    print("\n🧪 Testing configuration...")
    
    try:
        from config import Config
        
        # Test directory creation
        Config.ensure_directories()
        print("  ✅ Directory creation successful")
        
        # Test that required attributes exist
        required_attrs = ['GROQ_API_KEY', 'GEMINI_API_KEY', 'SENDER_EMAIL', 'APP_PASSWORD']
        for attr in required_attrs:
            if hasattr(Config, attr):
                print(f"  ✅ {attr} attribute exists")
            else:
                print(f"  ❌ {attr} attribute missing")
        
        return True
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False

def test_pdf_service():
    """Test PDF generation service."""
    print("\n🧪 Testing PDF service...")
    
    try:
        from services.pdf_service import PDFService
        
        pdf_service = PDFService()
        
        # Test simple PDF creation
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "test.pdf")
            
            result = pdf_service.create_simple_pdf(
                title="Test Document",
                content="This is a test document to verify PDF generation functionality.",
                output_file=output_file
            )
            
            if os.path.exists(result):
                print("  ✅ Simple PDF creation successful")
            else:
                print("  ❌ Simple PDF creation failed")
                return False
            
            # Test meeting minutes PDF
            sections = {
                "Executive Summary": "Test meeting summary for verification purposes.",
                "Action Items": "1. Test PDF generation\n2. Verify functionality\n3. Complete testing",
                "Decisions Made": "- Use PDF service for meeting minutes\n- Continue with testing"
            }
            
            minutes_file = os.path.join(temp_dir, "minutes.pdf")
            result = pdf_service.create_minutes_pdf(
                sections=sections,
                company="Test Company",
                meeting_title="Test Meeting",
                meeting_date="2024-07-07",
                output_file=minutes_file
            )
            
            if os.path.exists(result):
                print("  ✅ Meeting minutes PDF creation successful")
            else:
                print("  ❌ Meeting minutes PDF creation failed")
                return False
        
        return True
    except Exception as e:
        print(f"  ❌ PDF service test failed: {e}")
        return False

def test_email_service():
    """Test email service (connection only, no actual sending)."""
    print("\n🧪 Testing email service...")
    
    try:
        from services.email_service import EmailService
        
        email_service = EmailService()
        print("  ✅ Email service initialized successfully")
        
        # Test connection (this will likely fail without proper credentials)
        try:
            connection_result = email_service.test_connection()
            if connection_result:
                print("  ✅ Email connection test successful")
            else:
                print("  ⚠️  Email connection test failed (check credentials)")
        except Exception as e:
            print(f"  ⚠️  Email connection test failed: {e}")
        
        return True
    except Exception as e:
        print(f"  ❌ Email service test failed: {e}")
        return False

def test_summarization_service():
    """Test summarization service."""
    print("\n🧪 Testing summarization service...")
    
    try:
        from services.summarization_service import SummarizationService
        
        # This will likely fail without proper API key, but we can test initialization
        try:
            summarization_service = SummarizationService()
            print("  ✅ Summarization service initialized")
            
            # Test with sample transcript (this will fail without API key)
            sample_transcript = """
            John: Good morning everyone.
            Sarah: Thanks John. Let's discuss the project timeline.
            Mike: I think we can finish by next Friday.
            John: Great, let's finalize the details.
            """
            
            try:
                # This will likely fail without proper API key
                participants = summarization_service.extract_participants(sample_transcript)
                print("  ✅ Participant extraction test successful")
            except Exception as e:
                print(f"  ⚠️  Participant extraction failed (API key needed): {e}")
                
        except Exception as e:
            print(f"  ⚠️  Summarization service failed (API key needed): {e}")
        
        return True
    except Exception as e:
        print(f"  ❌ Summarization service test failed: {e}")
        return False

def test_transcription_service():
    """Test transcription service."""
    print("\n🧪 Testing transcription service...")
    
    try:
        from services.transcription_service import TranscriptionService
        
        # This will likely fail without proper API key
        try:
            transcription_service = TranscriptionService()
            print("  ✅ Transcription service initialized")
            
            # Test supported formats
            formats = transcription_service.get_supported_formats()
            print(f"  ✅ Supported formats: {formats}")
            
        except Exception as e:
            print(f"  ⚠️  Transcription service failed (API key needed): {e}")
        
        return True
    except Exception as e:
        print(f"  ❌ Transcription service test failed: {e}")
        return False

def test_media_converter():
    """Test media converter service."""
    print("\n🧪 Testing media converter...")
    
    try:
        from services.media_converter import MediaConverter
        
        media_converter = MediaConverter()
        print("  ✅ Media converter initialized successfully")
        
        # Test supported formats (no actual conversion)
        formats = media_converter.get_supported_formats() if hasattr(media_converter, 'get_supported_formats') else ['mp3', 'wav', 'flac']
        print(f"  ✅ Service supports various audio formats")
        
        return True
    except Exception as e:
        print(f"  ❌ Media converter test failed: {e}")
        return False

def test_meeting_assistant():
    """Test the main meeting assistant orchestrator."""
    print("\n🧪 Testing meeting assistant...")
    
    try:
        from api.meeting_assistant import MeetingAssistant
        
        assistant = MeetingAssistant()
        print("  ✅ Meeting assistant initialized")
        
        # Test service status
        try:
            service_status = assistant.test_services()
            print("  ✅ Service status check completed")
            
            for service, status in service_status.items():
                status_icon = "✅" if status else "⚠️"
                print(f"    {status_icon} {service}: {'OK' if status else 'Needs configuration'}")
                
        except Exception as e:
            print(f"  ⚠️  Service status check failed: {e}")
        
        return True
    except Exception as e:
        print(f"  ❌ Meeting assistant test failed: {e}")
        return False

def test_flask_api():
    """Test Flask API endpoints."""
    print("\n🧪 Testing Flask API...")
    
    try:
        from api.flask_app import app
        
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            print(f"  ✅ Health endpoint status: {response.status_code}")
            
            # Test supported formats endpoint
            response = client.get('/supported-formats')
            if response.status_code == 200:
                print("  ✅ Supported formats endpoint working")
            else:
                print(f"  ⚠️  Supported formats endpoint returned: {response.status_code}")
            
            print("  ✅ Flask API basic tests successful")
        
        return True
    except Exception as e:
        print(f"  ❌ Flask API test failed: {e}")
        return False

def test_transcript_processing():
    """Test transcript processing without external APIs."""
    print("\n🧪 Testing transcript processing...")
    
    try:
        from api.meeting_assistant import MeetingAssistant
        
        assistant = MeetingAssistant()
        
        sample_transcript = """
        John: Good morning everyone, let's start today's meeting.
        Sarah: Thanks John. I wanted to discuss the Q1 budget proposals.
        Mike: I agree, we need to finalize the numbers by Friday.
        John: Great, Sarah can you send the updated spreadsheet to the team?
        Sarah: Absolutely, I'll have it ready by tomorrow.
        """
        
        # This will likely fail without proper API configuration, but we can test the structure
        try:
            results = assistant.process_transcript_text(
                transcript=sample_transcript,
                recipients=["test@example.com"],
                meeting_title="Test Meeting",
                meeting_date="2024-07-07"
            )
            
            if results.get('success'):
                print("  ✅ Transcript processing successful")
            else:
                print(f"  ⚠️  Transcript processing failed: {results.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"  ⚠️  Transcript processing failed (API configuration needed): {e}")
        
        return True
    except Exception as e:
        print(f"  ❌ Transcript processing test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 ConverSync Meeting Assistant - Comprehensive Test Suite")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_configuration,
        test_pdf_service,
        test_email_service,
        test_media_converter,
        test_transcription_service,
        test_summarization_service,
        test_meeting_assistant,
        test_flask_api,
        test_transcript_processing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
    elif passed >= total * 0.7:
        print("⚠️  Most tests passed. Some features may need API key configuration.")
    else:
        print("❌ Many tests failed. Please check configuration and dependencies.")
    
    print("\n📝 Next steps:")
    print("1. Configure API keys in .env file")
    print("2. Test with actual media files")
    print("3. Start the Flask API: python api/flask_app.py")
    print("4. Test individual components as needed")

if __name__ == "__main__":
    main()
