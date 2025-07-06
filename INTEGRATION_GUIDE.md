# ConverSync Integration Guide

This guide explains how to use the fully integrated ConverSync meeting assistant with frontend and backend communication.

## Features

### 🚀 Complete Workflow
1. **Upload Meeting Recording**: Upload video/audio files via the web interface
2. **Automatic Transcription**: Files are converted to audio and transcribed using Groq
3. **AI Chat Interface**: Chat with Gemini about meeting content using the transcript as context
4. **PDF Generation**: Generate comprehensive meeting minutes as PDF
5. **Email Distribution**: Send meeting minutes to participants automatically

### 🎯 Key Capabilities
- **Smart Meeting Minutes**: Automatically generate comprehensive meeting summaries
- **Automated Mail Service**: Send personalized follow-up emails to participants
- **Follow-Up Questions**: Ask detailed questions about meeting content
- **Multi-format Support**: Supports video (mp4, avi, mov, mkv, wmv) and audio (mp3, wav, flac, m4a, ogg, webm)

## How to Use

### 1. Start the Backend Server
```bash
cd "c:\Users\akki\Documents\Projects\conversync"
python -m api.flask_app
```

The server will start at `http://localhost:5000`

### 2. Open the Frontend
Open `frontend/app.html` in your web browser. The page will connect to the backend automatically.

### 3. Upload a Meeting Recording
1. Click on the upload area or drag and drop your meeting recording
2. Click "Upload" to process the file
3. The system will:
   - Convert video to audio (if needed)
   - Transcribe the audio using Groq
   - Start a chat session with the transcript as context

### 4. Chat with Your Meeting Assistant
Once processing is complete, you'll be taken to the chat interface where you can:

#### Ask Questions
- "What were the main decisions made in the meeting?"
- "Who was assigned the task of updating the project timeline?"
- "What are the action items and their deadlines?"
- "Can you summarize the discussion about the budget?"

#### Generate PDF Minutes
1. Click "📄 Generate PDF"
2. Fill in meeting details:
   - Meeting Title
   - Meeting Date
   - Company Name
3. Click "Generate PDF" to create and download the document

#### Send Email to Participants
1. Click "📧 Send Email"
2. Fill in the details:
   - Meeting Title, Date, Company Name
   - Recipients (comma-separated email addresses)
   - Custom Message (optional)
3. Click "Send Email" to distribute the minutes

## API Endpoints

### File Processing
- `POST /transcribe-only` - Transcribe audio/video file
- `POST /process-video` - Complete video processing with email
- `POST /process-audio` - Complete audio processing with email

### Chat Interface
- `POST /chat/start` - Start new chat session with transcript
- `POST /chat/{session_id}/message` - Send message in chat session
- `POST /chat/{session_id}/generate-minutes` - Generate PDF minutes
- `POST /chat/{session_id}/send-email` - Send meeting minutes via email
- `GET /chat/{session_id}/history` - Get chat history

### Utilities
- `GET /health` - Health check
- `GET /supported-formats` - Get supported file formats
- `GET /download/{filename}` - Download generated files

## File Structure

```
conversync/
├── frontend/
│   ├── app.html          # Main integrated frontend
│   └── bot.html          # Original chat interface
├── api/
│   ├── flask_app.py      # Main Flask application with chat endpoints
│   └── meeting_assistant.py # Core business logic
├── services/             # Core services
│   ├── transcription_service.py
│   ├── summarization_service.py
│   ├── pdf_service.py
│   └── email_service.py
└── config/              # Configuration
    └── settings.py
```

## Technical Details

### Frontend Integration
- **File Upload**: Drag-and-drop interface with progress indication
- **Real-time Chat**: WebSocket-style communication with typing indicators
- **Modal Dialogs**: For PDF generation and email sending
- **Responsive Design**: Works on desktop and mobile devices

### Backend Architecture
- **Session Management**: Each transcript gets a unique chat session
- **Context-Aware AI**: Gemini responses are based on meeting transcript
- **File Processing Pipeline**: Video → Audio → Transcript → Chat Context
- **Email Integration**: Automatic PDF generation and distribution

### Security Features
- **File Size Limits**: 500MB maximum upload size
- **File Type Validation**: Only allowed audio/video formats
- **Session Isolation**: Each chat session is independent
- **CORS Protection**: Proper cross-origin request handling

## Configuration Requirements

Ensure these environment variables are set:
- `GROQ_API_KEY` - For transcription service
- `GEMINI_API_KEY` - For AI chat responses
- `SENDER_EMAIL` - For sending meeting minutes
- `APP_PASSWORD` - For email authentication

## Troubleshooting

### Common Issues

1. **CORS Errors**: Make sure the backend server is running on localhost:5000
2. **Upload Failures**: Check file format and size (max 500MB)
3. **Transcription Errors**: Verify GROQ_API_KEY is valid
4. **Chat Errors**: Verify GEMINI_API_KEY is valid
5. **Email Errors**: Check email credentials and recipient addresses

### Error Messages
- "No valid audio or video file provided" - Upload a supported file format
- "Invalid or expired session" - Start a new session by uploading a file
- "Failed to start chat session" - Check backend server and API keys

## Next Steps

1. **Customize the UI**: Modify `frontend/app.html` for your branding
2. **Add Authentication**: Implement user login and session management
3. **Database Integration**: Store chat sessions and meeting data
4. **Advanced Features**: Add speaker identification, sentiment analysis
5. **Mobile App**: Create native mobile applications using the API

## Support

For issues or questions:
1. Check the console for error messages
2. Verify all environment variables are set
3. Ensure all dependencies are installed
4. Check the Flask server logs for backend errors
