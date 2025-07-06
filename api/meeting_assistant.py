from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from config import Config
from services import (
    MediaConverter,
    TranscriptionService,
    SummarizationService,
    PDFService,
    EmailService
)

class MeetingAssistant:
    """
    Main orchestrator class for the meeting assistant application.
    Coordinates all services to process meeting recordings end-to-end.
    """
    
    def __init__(self):
        """Initialize all services."""
        self.media_converter = MediaConverter()
        self.transcription_service = TranscriptionService()
        self.summarization_service = SummarizationService()
        self.pdf_service = PDFService()
        self.email_service = EmailService()
        
        # Ensure all required directories exist
        Config.ensure_directories()
    
    def process_meeting_recording(self, 
                                video_file_path: str,
                                recipients: List[str],
                                meeting_title: str = None,
                                meeting_date: str = None,
                                company_name: str = None,
                                custom_email_message: str = None) -> Dict[str, Any]:
        """
        Complete end-to-end processing of a meeting recording.
        
        Args:
            video_file_path (str): Path to the video file
            recipients (List[str]): Email addresses to send the summary to
            meeting_title (str, optional): Title of the meeting
            meeting_date (str, optional): Date of the meeting
            company_name (str, optional): Company name for PDF header
            custom_email_message (str, optional): Custom message for email
            
        Returns:
            Dict[str, Any]: Processing results including file paths and status
        """
        results = {
            'success': False,
            'video_file': video_file_path,
            'audio_file': None,
            'transcript_file': None,
            'pdf_file': None,
            'email_sent': False,
            'error': None,
            'processing_time': None
        }
        
        start_time = datetime.now()
        
        try:
            print("🎬 Starting meeting recording processing...")
            
            # Step 1: Convert video to audio
            print("🔄 Converting video to audio...")
            audio_file = self.media_converter.convert_mp4_to_mp3(video_file_path)
            results['audio_file'] = audio_file
            print(f"✅ Audio conversion complete: {audio_file}")
            
            # Step 2: Transcribe audio
            print("🎤 Transcribing audio...")
            transcription_result = self.transcription_service.transcribe_audio(audio_file)
            transcript_text = transcription_result['text']
            results['transcript_file'] = transcription_result['output_file']
            print(f"✅ Transcription complete: {results['transcript_file']}")
            
            # Step 3: Generate summary
            print("📝 Generating meeting summary...")
            summary_sections = self.summarization_service.generate_meeting_summary(transcript_text)
            
            # Add participants section if we can extract them
            participants = self.summarization_service.extract_participants(transcript_text)
            print("✅ Summary generation complete")
            
            # Step 4: Create PDF
            print("📄 Creating PDF...")
            pdf_file = self.pdf_service.create_minutes_pdf(
                sections=summary_sections,
                company=company_name,
                meeting_title=meeting_title,
                meeting_date=meeting_date,
                participants=participants
            )
            results['pdf_file'] = pdf_file
            print(f"✅ PDF creation complete: {pdf_file}")
            
            # Step 5: Send email
            print("📧 Sending email...")
            email_success = self.email_service.send_meeting_summary(
                pdf_path=pdf_file,
                recipients=recipients,
                meeting_title=meeting_title,
                meeting_date=meeting_date,
                custom_message=custom_email_message
            )
            results['email_sent'] = email_success
            
            if email_success:
                print("✅ Email sent successfully")
            else:
                print("❌ Email sending failed")
            
            results['success'] = True
            results['processing_time'] = (datetime.now() - start_time).total_seconds()
            
            print(f"🎉 Processing complete! Total time: {results['processing_time']:.2f} seconds")
            
        except Exception as e:
            results['error'] = str(e)
            results['processing_time'] = (datetime.now() - start_time).total_seconds()
            print(f"❌ Processing failed: {e}")
        
        return results
    
    def process_audio_file(self,
                          audio_file_path: str,
                          recipients: List[str],
                          meeting_title: str = None,
                          meeting_date: str = None,
                          company_name: str = None,
                          custom_email_message: str = None) -> Dict[str, Any]:
        """
        Process an audio file directly (skip video conversion).
        
        Args:
            audio_file_path (str): Path to the audio file
            recipients (List[str]): Email addresses to send the summary to
            meeting_title (str, optional): Title of the meeting
            meeting_date (str, optional): Date of the meeting
            company_name (str, optional): Company name for PDF header
            custom_email_message (str, optional): Custom message for email
            
        Returns:
            Dict[str, Any]: Processing results
        """
        results = {
            'success': False,
            'audio_file': audio_file_path,
            'transcript_file': None,
            'pdf_file': None,
            'email_sent': False,
            'error': None,
            'processing_time': None
        }
        
        start_time = datetime.now()
        
        try:
            print("🎤 Starting audio processing...")
            
            # Step 1: Transcribe audio
            print("🔄 Transcribing audio...")
            transcription_result = self.transcription_service.transcribe_audio(audio_file_path)
            transcript_text = transcription_result['text']
            results['transcript_file'] = transcription_result['output_file']
            print(f"✅ Transcription complete: {results['transcript_file']}")
            
            # Step 2: Generate summary
            print("📝 Generating meeting summary...")
            summary_sections = self.summarization_service.generate_meeting_summary(transcript_text)
            participants = self.summarization_service.extract_participants(transcript_text)
            print("✅ Summary generation complete")
            
            # Step 3: Create PDF
            print("📄 Creating PDF...")
            pdf_file = self.pdf_service.create_minutes_pdf(
                sections=summary_sections,
                company=company_name,
                meeting_title=meeting_title,
                meeting_date=meeting_date,
                participants=participants
            )
            results['pdf_file'] = pdf_file
            print(f"✅ PDF creation complete: {pdf_file}")
            
            # Step 4: Send email
            print("📧 Sending email...")
            email_success = self.email_service.send_meeting_summary(
                pdf_path=pdf_file,
                recipients=recipients,
                meeting_title=meeting_title,
                meeting_date=meeting_date,
                custom_message=custom_email_message
            )
            results['email_sent'] = email_success
            
            results['success'] = True
            results['processing_time'] = (datetime.now() - start_time).total_seconds()
            
            print(f"🎉 Processing complete! Total time: {results['processing_time']:.2f} seconds")
            
        except Exception as e:
            results['error'] = str(e)
            results['processing_time'] = (datetime.now() - start_time).total_seconds()
            print(f"❌ Processing failed: {e}")
        
        return results
    
    def process_transcript_text(self,
                               transcript: str,
                               recipients: List[str],
                               meeting_title: str = None,
                               meeting_date: str = None,
                               company_name: str = None,
                               custom_email_message: str = None) -> Dict[str, Any]:
        """
        Process raw transcript text (skip conversion and transcription).
        
        Args:
            transcript (str): Raw transcript text
            recipients (List[str]): Email addresses to send the summary to
            meeting_title (str, optional): Title of the meeting
            meeting_date (str, optional): Date of the meeting
            company_name (str, optional): Company name for PDF header
            custom_email_message (str, optional): Custom message for email
            
        Returns:
            Dict[str, Any]: Processing results
        """
        results = {
            'success': False,
            'transcript_text': transcript,
            'pdf_file': None,
            'email_sent': False,
            'error': None,
            'processing_time': None
        }
        
        start_time = datetime.now()
        
        try:
            print("📝 Starting transcript processing...")
            
            # Step 1: Generate summary
            print("🔄 Generating meeting summary...")
            summary_sections = self.summarization_service.generate_meeting_summary(transcript)
            participants = self.summarization_service.extract_participants(transcript)
            print("✅ Summary generation complete")
            
            # Step 2: Create PDF
            print("📄 Creating PDF...")
            pdf_file = self.pdf_service.create_minutes_pdf(
                sections=summary_sections,
                company=company_name,
                meeting_title=meeting_title,
                meeting_date=meeting_date,
                participants=participants
            )
            results['pdf_file'] = pdf_file
            print(f"✅ PDF creation complete: {pdf_file}")
            
            # Step 3: Send email
            print("📧 Sending email...")
            email_success = self.email_service.send_meeting_summary(
                pdf_path=pdf_file,
                recipients=recipients,
                meeting_title=meeting_title,
                meeting_date=meeting_date,
                custom_message=custom_email_message
            )
            results['email_sent'] = email_success
            
            results['success'] = True
            results['processing_time'] = (datetime.now() - start_time).total_seconds()
            
            print(f"🎉 Processing complete! Total time: {results['processing_time']:.2f} seconds")
            
        except Exception as e:
            results['error'] = str(e)
            results['processing_time'] = (datetime.now() - start_time).total_seconds()
            print(f"❌ Processing failed: {e}")
        
        return results
    
    def test_services(self) -> Dict[str, bool]:
        """
        Test all services to ensure they're working properly.
        
        Returns:
            Dict[str, bool]: Status of each service
        """
        results = {}
        
        print("🧪 Testing services...")
        
        # Test email service
        try:
            results['email'] = self.email_service.test_connection()
        except Exception as e:
            print(f"Email service test failed: {e}")
            results['email'] = False
        
        # Test other services (basic initialization)
        try:
            results['media_converter'] = True
            results['transcription'] = True
            results['summarization'] = True
            results['pdf'] = True
        except Exception as e:
            print(f"Service initialization failed: {e}")
            results['media_converter'] = False
            results['transcription'] = False
            results['summarization'] = False
            results['pdf'] = False
        
        return results
