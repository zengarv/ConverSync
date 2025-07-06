# ConverSync - Meeting Assistant

A comprehensive meeting assistant that automatically processes meeting recordings, generates transcripts, creates summaries, and emails meeting minutes to participants.

## Features

- **Video to Audio Conversion**: Convert MP4 videos to MP3 audio files
- **Audio Transcription**: Transcribe audio using Groq's Whisper API
- **AI Summarization**: Generate structured meeting summaries using Google's Gemini AI
- **PDF Generation**: Create professional meeting minutes PDFs
- **Email Integration**: Automatically send meeting minutes to participants
- **RESTful API**: Flask-based API for web application integration

## Project Structure

```
conversync/
├── api/
│   ├── __init__.py
│   ├── flask_app.py          # Flask web API
│   └── meeting_assistant.py  # Main orchestrator class
├── config/
│   ├── __init__.py
│   └── settings.py           # Configuration management
├── services/
│   ├── __init__.py
│   ├── media_converter.py    # Video/audio conversion
│   ├── transcription_service.py  # Audio transcription
│   ├── summarization_service.py  # AI summarization
│   ├── pdf_service.py        # PDF generation
│   └── email_service.py      # Email functionality
├── uploads/                  # Upload directory (created automatically)
├── outputs/                  # Output directory (created automatically)
├── temp/                     # Temporary files (created automatically)
├── .env                      # Environment variables
├── .env.example              # Environment variables template
├── requirements.txt          # Python dependencies
├── example_usage.py          # Usage examples
├── backend_funcs.py          # Original functions (deprecated)
└── README.md                 # This file
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd conversync
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   - Copy `.env.example` to `.env`
   - Fill in your API keys and email configuration:
   ```bash
   cp .env.example .env
   ```

4. **Configure your `.env` file**:
   ```env
   # API Keys
   GROQ_API_KEY=your_groq_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here

   # Email Configuration
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=your_email@gmail.com
   SENDER_NAME=conversync
   APP_PASSWORD=your_app_password_here

   # Other settings...
   ```

## API Keys Setup

### Groq API Key
1. Visit [Groq Console](https://console.groq.com/)
2. Sign up/login and create an API key
3. Add it to your `.env` file as `GROQ_API_KEY`

### Google Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file as `GEMINI_API_KEY`

### Gmail App Password
1. Enable 2-factor authentication on your Gmail account
2. Generate an app password: [Google Account Settings](https://myaccount.google.com/apppasswords)
3. Add it to your `.env` file as `APP_PASSWORD`

## Usage

### As a Python Module

```python
from api.meeting_assistant import MeetingAssistant

# Initialize the assistant
assistant = MeetingAssistant()

# Process a video file
results = assistant.process_meeting_recording(
    video_file_path="meeting.mp4",
    recipients=["user1@example.com", "user2@example.com"],
    meeting_title="Weekly Standup",
    meeting_date="2024-01-15",
    company_name="Your Company"
)

print(f"Success: {results['success']}")
print(f"PDF generated: {results['pdf_file']}")
```

### As a Web API

1. **Start the Flask server**:
   ```bash
   python api/flask_app.py
   ```

2. **API Endpoints**:

   - **Health Check**: `GET /health`
   - **Process Video**: `POST /process-video`
   - **Process Audio**: `POST /process-audio`
   - **Process Transcript**: `POST /process-transcript`
   - **Transcribe Only**: `POST /transcribe-only`
   - **Download File**: `GET /download/<filename>`
   - **Supported Formats**: `GET /supported-formats`

3. **Example API Usage**:

   ```bash
   # Process a video file
   curl -X POST \
     -F "video_file=@meeting.mp4" \
     -F "recipients=user1@example.com,user2@example.com" \
     -F "meeting_title=Weekly Standup" \
     -F "meeting_date=2024-01-15" \
     http://localhost:5000/process-video
   ```

   ```bash
   # Process raw transcript
   curl -X POST \
     -H "Content-Type: application/json" \
     -d '{
       "transcript": "Meeting transcript text here...",
       "recipients": ["user1@example.com", "user2@example.com"],
       "meeting_title": "Budget Review",
       "meeting_date": "2024-01-15"
     }' \
     http://localhost:5000/process-transcript
   ```

## API Reference

### Process Video Recording
**POST** `/process-video`

Process a video file to generate meeting minutes.

**Form Data:**
- `video_file` (file): Video file (MP4, AVI, MOV, MKV, WMV)
- `recipients` (string): Comma-separated email addresses
- `meeting_title` (string, optional): Meeting title
- `meeting_date` (string, optional): Meeting date
- `company_name` (string, optional): Company name for PDF header
- `custom_message` (string, optional): Custom email message

**Response:**
```json
{
  "success": true,
  "video_file": "/path/to/video.mp4",
  "audio_file": "/path/to/audio.mp3",
  "transcript_file": "/path/to/transcript.txt",
  "pdf_file": "/path/to/minutes.pdf",
  "email_sent": true,
  "processing_time": 45.67
}
```

### Process Audio File
**POST** `/process-audio`

Process an audio file to generate meeting minutes.

**Form Data:**
- `audio_file` (file): Audio file (MP3, WAV, FLAC, M4A, OGG, WEBM)
- `recipients` (string): Comma-separated email addresses
- `meeting_title` (string, optional): Meeting title
- `meeting_date` (string, optional): Meeting date
- `company_name` (string, optional): Company name for PDF header
- `custom_message` (string, optional): Custom email message

### Process Transcript Text
**POST** `/process-transcript`

Process raw transcript text to generate meeting minutes.

**JSON Body:**
```json
{
  "transcript": "Meeting transcript text...",
  "recipients": ["user1@example.com", "user2@example.com"],
  "meeting_title": "Optional meeting title",
  "meeting_date": "Optional meeting date",
  "company_name": "Optional company name",
  "custom_message": "Optional custom message"
}
```

### Transcribe Only
**POST** `/transcribe-only`

Transcribe audio/video file without generating summary.

**Form Data:**
- `video_file` OR `audio_file` (file): Media file to transcribe

**Response:**
```json
{
  "success": true,
  "transcript": "Transcribed text...",
  "language": "en",
  "duration": 123.45,
  "output_file": "/path/to/transcript.txt"
}
```

## Services Overview

### MediaConverter
- Convert video files to audio
- Support for multiple video formats
- Get video information (duration, size, etc.)

### TranscriptionService
- Transcribe audio using Groq's Whisper API
- Support for multiple audio formats
- Batch transcription capabilities

### SummarizationService
- Generate structured meeting summaries using Gemini AI
- Extract participants, decisions, action items
- Custom summarization prompts

### PDFService
- Create professional meeting minutes PDFs
- Customizable headers and company branding
- Multi-page support with pagination

### EmailService
- Send emails with PDF attachments
- Customizable email templates
- Support for multiple recipients

## Configuration

All configuration is managed through environment variables and the `Config` class in `config/settings.py`. Key settings include:

- **API Keys**: Groq and Gemini API keys
- **Email Settings**: SMTP configuration
- **File Paths**: Upload, output, and temporary directories
- **Model Settings**: AI model selection
- **PDF Settings**: Company branding options

## Error Handling

The application includes comprehensive error handling:
- Invalid file formats
- Missing API keys
- Network connectivity issues
- File processing errors
- Email delivery failures

## Development

### Running Tests
```bash
python example_usage.py
```

### Development Server
```bash
python api/flask_app.py
```

The Flask development server will run on `http://localhost:5000` with debug mode enabled.

## Supported File Formats

### Video Files
- MP4, AVI, MOV, MKV, WMV

### Audio Files
- MP3, WAV, FLAC, M4A, OGG, WEBM

## Limitations

- Maximum file size: 500MB
- Video processing requires sufficient disk space
- API rate limits apply to external services
- Email sending requires proper SMTP configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the configuration in your `.env` file
2. Verify API keys are valid
3. Check network connectivity
4. Review log outputs for specific error messages
