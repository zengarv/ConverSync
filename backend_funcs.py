"""
ConverSync Meeting Assistant - Legacy Backend Functions
========================================================

This file maintains backward compatibility with the original backend functions.
For new development, please use the structured services in the 'services' directory
and the main API in 'api/meeting_assistant.py'.

The functions below are now wrappers around the new structured services.
"""

import warnings
from pathlib import Path

# Import the new structured services
try:
    from services import (
        MediaConverter, 
        TranscriptionService, 
        SummarizationService, 
        PDFService, 
        EmailService
    )
    from api.meeting_assistant import MeetingAssistant
    from config import Config
    
    # Initialize services
    _media_converter = MediaConverter()
    _transcription_service = TranscriptionService()
    _summarization_service = SummarizationService()
    _pdf_service = PDFService()
    _email_service = EmailService()
    _meeting_assistant = MeetingAssistant()
    
    SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import new services: {e}")
    print("Falling back to legacy implementation...")
    SERVICES_AVAILABLE = False

# Original imports for fallback
import os
try:
    from moviepy.editor import VideoFileClip
except ImportError:
    try:
        from moviepy import VideoFileClip
    except ImportError:
        VideoFileClip = None
from datetime import datetime

# Legacy function wrappers for backward compatibility
def convert_mp4_to_mp3(mp4_file_path, mp3_file_path=None):
    """
    Legacy wrapper for video to audio conversion.
    
    Args:
        mp4_file_path (str): The full path to the input MP4 video file.
        mp3_file_path (str): The full path where the output MP3 audio file will be saved.
    """
    warnings.warn(
        "convert_mp4_to_mp3 is deprecated. Use services.MediaConverter.convert_mp4_to_mp3 instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    if SERVICES_AVAILABLE:
        return _media_converter.convert_mp4_to_mp3(mp4_file_path, mp3_file_path)
    else:
        # Fallback to original implementation
        if VideoFileClip is None:
            print("Error: MoviePy not available. Cannot convert video files.")
            return
            
        if not os.path.exists(mp4_file_path):
            print(f"Error: MP4 file not found at '{mp4_file_path}'")
            return

        try:
            video_clip = VideoFileClip(mp4_file_path)
            audio_clip = video_clip.audio
            
            if mp3_file_path is None:
                mp3_file_path = str(Path(mp4_file_path).with_suffix('.mp3'))
            
            audio_clip.write_audiofile(mp3_file_path)
            audio_clip.close()
            video_clip.close()
            
            print(f"Successfully converted '{mp4_file_path}' to '{mp3_file_path}'")
            return mp3_file_path

        except Exception as e:
            print(f"An error occurred during conversion: {e}")

def transcribe_audio(audio_file_path, output_file_path=None):
    """
    Legacy wrapper for audio transcription.
    
    Args:
        audio_file_path (str): Path to the audio file.
        output_file_path (str, optional): Path to save the transcription.
    
    Returns:
        str: Transcribed text.
    """
    warnings.warn(
        "transcribe_audio is deprecated. Use services.TranscriptionService.transcribe_audio instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    if SERVICES_AVAILABLE:
        result = _transcription_service.transcribe_audio(audio_file_path, output_file_path)
        return result['text']
    else:
        print("Error: New transcription service not available. Please install required dependencies.")
        return None

def gpt(prompt: str) -> str:
    """
    Legacy wrapper for Gemini AI.
    
    Args:
        prompt (str): The prompt to send to Gemini.
    
    Returns:
        str: Generated response.
    """
    warnings.warn(
        "gpt function is deprecated. Use services.SummarizationService methods instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    if SERVICES_AVAILABLE:
        return _summarization_service._gpt(prompt)
    else:
        print("Error: New summarization service not available. Please install required dependencies.")
        return ""

def create_minutes_pdf(sections: dict,
                       company: str = "",
                       logo_path: str = None,
                       output_file: str = "minutes_of_meeting.pdf"):
    """
    Legacy wrapper for PDF creation.
    
    Args:
        sections (dict): Dictionary of sections for the PDF.
        company (str): Company name.
        logo_path (str): Path to company logo.
        output_file (str): Output PDF file path.
    """
    warnings.warn(
        "create_minutes_pdf is deprecated. Use services.PDFService.create_minutes_pdf instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    if SERVICES_AVAILABLE:
        return _pdf_service.create_minutes_pdf(
            sections=sections,
            company=company,
            logo_path=logo_path,
            output_file=output_file
        )
    else:
        print("Error: New PDF service not available. Please install required dependencies.")

def send_email_with_pdf(pdf_path, subject, body, recipients):
    """
    Legacy wrapper for sending emails with PDF attachments.
    
    Args:
        pdf_path (str): Path to PDF file.
        subject (str): Email subject.
        body (str): Email body.
        recipients (list): List of recipient email addresses.
    """
    warnings.warn(
        "send_email_with_pdf is deprecated. Use services.EmailService.send_email_with_pdf instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    if SERVICES_AVAILABLE:
        return _email_service.send_email_with_pdf(
            pdf_path=pdf_path,
            recipients=recipients,
            subject=subject,
            body=body
        )
    else:
        print("Error: New email service not available. Please install required dependencies.")

def process_meeting_end_to_end(video_file_path, recipients, meeting_title=None, meeting_date=None):
    """
    Process a meeting recording from start to finish.
    
    Args:
        video_file_path (str): Path to the video file.
        recipients (list): List of email addresses.
        meeting_title (str, optional): Meeting title.
        meeting_date (str, optional): Meeting date.
    
    Returns:
        dict: Processing results.
    """
    if SERVICES_AVAILABLE:
        return _meeting_assistant.process_meeting_recording(
            video_file_path=video_file_path,
            recipients=recipients,
            meeting_title=meeting_title,
            meeting_date=meeting_date
        )
    else:
        print("Error: New meeting assistant not available. Please install required dependencies.")
        return {'success': False, 'error': 'Services not available'}

# Legacy configuration (for backward compatibility)
API_KEY = "AIzaSyC7_jEsLwr7clATLPOWG9b4-GBFG7FEap8"
MODEL = "gemini-2.5-flash"
OUTPUT_PDF = "minutes_of_meeting.pdf"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "conversync.ai@gmail.com"
SENDER_NAME = "conversync"
APP_PASSWORD = "oexojcabxxwxxppk"
PDF_PATH = "minutes_of_meeting.pdf"
SUBJECT = "Minutes of the Meeting"
BODY = """
Dear Team,

Attached are the minutes of the recent meeting. Please review and follow up on your respective action items.

Regards,
Meeting Assistant Bot
"""
RECIPIENTS = ["ee2300020@iiti.ac.in"]

# Main execution (for backward compatibility)
if __name__ == "__main__":
    print("=" * 60)
    print("ConverSync Meeting Assistant - Legacy Backend")
    print("=" * 60)
    print()
    print("⚠️  WARNING: You are using the legacy backend functions.")
    print("   For better functionality, please use:")
    print("   • python main.py - to test the new services")
    print("   • python api/flask_app.py - to start the web API")
    print("   • See example_usage.py for the new Python API")
    print()
    
    if SERVICES_AVAILABLE:
        print("✅ New services are available! Consider migrating your code.")
        print("   The new structured approach provides better error handling,")
        print("   logging, and maintainability.")
    else:
        print("❌ New services are not available. Please install dependencies:")
        print("   pip install -r requirements.txt")
    
    print()
    print("=" * 60)
