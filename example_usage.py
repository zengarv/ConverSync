"""
Example usage of the Meeting Assistant API
"""

from api.meeting_assistant import MeetingAssistant

def main():
    # Initialize the meeting assistant
    assistant = MeetingAssistant()
    
    # Test services
    print("Testing services...")
    service_status = assistant.test_services()
    print("Service Status:", service_status)
    
    # Example 1: Process a video file
    print("\n" + "="*50)
    print("Example 1: Processing video file")
    print("="*50)
    
    # Note: Replace with actual file paths and email addresses
    video_file = "path/to/your/meeting.mp4"
    recipients = ["user1@example.com", "user2@example.com"]
    
    try:
        results = assistant.process_meeting_recording(
            video_file_path=video_file,
            recipients=recipients,
            meeting_title="Weekly Team Standup",
            meeting_date="2024-01-15",
            company_name="Your Company",
            custom_email_message="Please review the action items from today's standup."
        )
        
        print("Processing Results:")
        print(f"Success: {results['success']}")
        print(f"Audio file: {results['audio_file']}")
        print(f"Transcript file: {results['transcript_file']}")
        print(f"PDF file: {results['pdf_file']}")
        print(f"Email sent: {results['email_sent']}")
        print(f"Processing time: {results['processing_time']} seconds")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Process audio file directly
    print("\n" + "="*50)
    print("Example 2: Processing audio file")
    print("="*50)
    
    audio_file = "path/to/your/meeting.mp3"
    
    try:
        results = assistant.process_audio_file(
            audio_file_path=audio_file,
            recipients=recipients,
            meeting_title="Product Planning Meeting",
            meeting_date="2024-01-16"
        )
        
        print("Processing Results:")
        print(f"Success: {results['success']}")
        print(f"PDF file: {results['pdf_file']}")
        print(f"Email sent: {results['email_sent']}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: Process raw transcript
    print("\n" + "="*50)
    print("Example 3: Processing raw transcript")
    print("="*50)
    
    sample_transcript = """
    John: Good morning everyone, let's start today's meeting.
    Sarah: Thanks John. I wanted to discuss the Q1 budget proposals.
    Mike: I agree, we need to finalize the numbers by Friday.
    John: Great, Sarah can you send the updated spreadsheet to the team?
    Sarah: Absolutely, I'll have it ready by tomorrow.
    John: Perfect. Any other items to discuss?
    Mike: We should also plan the client presentation for next week.
    John: Good point. Let's schedule a prep meeting for Thursday.
    """
    
    try:
        results = assistant.process_transcript_text(
            transcript=sample_transcript,
            recipients=recipients,
            meeting_title="Budget Review Meeting",
            meeting_date="2024-01-17"
        )
        
        print("Processing Results:")
        print(f"Success: {results['success']}")
        print(f"PDF file: {results['pdf_file']}")
        print(f"Email sent: {results['email_sent']}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
