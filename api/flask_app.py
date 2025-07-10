from flask import Flask, request, jsonify, send_file, session, send_from_directory
from werkzeug.utils import secure_filename
import os
from pathlib import Path
import tempfile
import json
from datetime import datetime
import uuid

# Simple conversation memory implementation (will upgrade to LangChain later)
class ConversationMemory:
    """Simple conversation memory management."""
    
    def __init__(self, max_messages=20):
        self.messages = []
        self.max_messages = max_messages
    
    def add_user_message(self, message):
        """Add a user message to memory."""
        self.messages.append({
            'type': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        self._trim_memory()
    
    def add_ai_message(self, message):
        """Add an AI response to memory."""
        self.messages.append({
            'type': 'ai',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        self._trim_memory()
    
    def get_conversation_history(self):
        """Get formatted conversation history for context."""
        history = []
        for msg in self.messages:
            if msg['type'] == 'user':
                history.append(f"Human: {msg['content']}")
            else:
                history.append(f"Assistant: {msg['content']}")
        return "\n".join(history)
    
    def get_recent_context(self, num_messages=10):
        """Get recent conversation context."""
        recent = self.messages[-num_messages:] if len(self.messages) > num_messages else self.messages
        context = []
        for msg in recent:
            if msg['type'] == 'user':
                context.append(f"Human: {msg['content']}")
            else:
                context.append(f"Assistant: {msg['content']}")
        return "\n".join(context)
    
    def _trim_memory(self):
        """Keep memory within limits."""
        if len(self.messages) > self.max_messages:
            # Keep the first few messages for context and trim the middle
            self.messages = self.messages[:2] + self.messages[-(self.max_messages-2):]
    
    def clear(self):
        """Clear conversation memory."""
        self.messages = []
    
    def to_dict(self):
        """Convert memory to dictionary for storage."""
        return {
            'messages': self.messages,
            'max_messages': self.max_messages
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create memory from dictionary."""
        memory = cls(max_messages=data.get('max_messages', 20))
        memory.messages = data.get('messages', [])
        return memory

from api.meeting_assistant import MeetingAssistant
from services.tts_service import TTSService
from config import Config

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.secret_key = 'your-secret-key-change-this'  # Change this in production

# Initialize the meeting assistant
meeting_assistant = MeetingAssistant()

# Initialize TTS service
tts_service = TTSService()

# Store active chat sessions with conversation memory
chat_sessions = {}

# Allowed file extensions
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'flac', 'm4a', 'ogg', 'webm'}

# CORS handler
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    return response

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'status': 'OK'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        return response

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/', methods=['GET'])
def serve_frontend():
    """Serve the main React frontend application."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>', methods=['GET'])
def serve_static_files(path):
    """Serve static files from React build."""
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        # For client-side routing, serve index.html for unknown routes
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/api', methods=['GET'])
def api_info():
    """API information endpoint."""
    return jsonify({
        'message': 'ConverSync Meeting Assistant API',
        'version': '1.0.0',
        'frontend_url': 'http://localhost:5000/',
        'frontend_type': 'React with Vite',
        'features': {
            'conversation_memory': 'Enhanced conversation context using memory management',
            'meeting_analysis': 'AI-powered meeting transcript analysis',
            'multi_format_support': 'Video, audio, and text processing'
        },
        'endpoints': {
            'health': '/health',
            'process_video': '/process-video',
            'process_audio': '/process-audio',
            'process_transcript': '/process-transcript',
            'transcribe': '/transcribe-only',
            'chat_start': '/chat/start',
            'chat_message': '/chat/{session_id}/message',
            'chat_history': '/chat/{session_id}/history',
            'chat_memory': '/chat/{session_id}/memory',
            'chat_memory_clear': '/chat/{session_id}/memory/clear',
            'chat_memory_summary': '/chat/{session_id}/memory/summary',
            'generate_pdf': '/chat/{session_id}/generate-minutes',
            'send_email': '/chat/{session_id}/send-email',
            'tts': '/chat/{session_id}/tts',
            'supported_formats': '/supported-formats'
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        service_status = meeting_assistant.test_services()
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': service_status
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/process-video', methods=['POST'])
def process_video():
    """Process a video file for meeting minutes."""
    try:
        # Check if file is present
        if 'video_file' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename, ALLOWED_VIDEO_EXTENSIONS):
            return jsonify({'error': 'Invalid file type. Allowed: ' + ', '.join(ALLOWED_VIDEO_EXTENSIONS)}), 400
        
        # Get form data
        recipients = request.form.get('recipients', '').split(',')
        recipients = [email.strip() for email in recipients if email.strip()]
        
        if not recipients:
            return jsonify({'error': 'No recipients provided'}), 400
        
        meeting_title = request.form.get('meeting_title')
        meeting_date = request.form.get('meeting_date')
        company_name = request.form.get('company_name')
        custom_message = request.form.get('custom_message')
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, filename)
        file.save(file_path)
        
        # Process the video
        results = meeting_assistant.process_meeting_recording(
            video_file_path=file_path,
            recipients=recipients,
            meeting_title=meeting_title,
            meeting_date=meeting_date,
            company_name=company_name,
            custom_email_message=custom_message
        )
        
        # Clean up temporary file
        try:
            os.remove(file_path)
            os.rmdir(temp_dir)
        except:
            pass
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/process-audio', methods=['POST'])
def process_audio():
    """Process an audio file for meeting minutes."""
    try:
        # Check if file is present
        if 'audio_file' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        file = request.files['audio_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename, ALLOWED_AUDIO_EXTENSIONS):
            return jsonify({'error': 'Invalid file type. Allowed: ' + ', '.join(ALLOWED_AUDIO_EXTENSIONS)}), 400
        
        # Get form data
        recipients = request.form.get('recipients', '').split(',')
        recipients = [email.strip() for email in recipients if email.strip()]
        
        if not recipients:
            return jsonify({'error': 'No recipients provided'}), 400
        
        meeting_title = request.form.get('meeting_title')
        meeting_date = request.form.get('meeting_date')
        company_name = request.form.get('company_name')
        custom_message = request.form.get('custom_message')
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, filename)
        file.save(file_path)
        
        # Process the audio
        results = meeting_assistant.process_audio_file(
            audio_file_path=file_path,
            recipients=recipients,
            meeting_title=meeting_title,
            meeting_date=meeting_date,
            company_name=company_name,
            custom_email_message=custom_message
        )
        
        # Clean up temporary file
        try:
            os.remove(file_path)
            os.rmdir(temp_dir)
        except:
            pass
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/process-transcript', methods=['POST'])
def process_transcript():
    """Process raw transcript text for meeting minutes."""
    try:
        data = request.get_json()
        
        if not data or 'transcript' not in data:
            return jsonify({'error': 'No transcript text provided'}), 400
        
        transcript = data['transcript']
        recipients = data.get('recipients', [])
        
        if not recipients:
            return jsonify({'error': 'No recipients provided'}), 400
        
        meeting_title = data.get('meeting_title')
        meeting_date = data.get('meeting_date')
        company_name = data.get('company_name')
        custom_message = data.get('custom_message')
        
        # Process the transcript
        results = meeting_assistant.process_transcript_text(
            transcript=transcript,
            recipients=recipients,
            meeting_title=meeting_title,
            meeting_date=meeting_date,
            company_name=company_name,
            custom_email_message=custom_message
        )
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/transcribe-only', methods=['POST'])
def transcribe_only():
    """Transcribe audio/video file without generating summary."""
    try:
        file = None
        file_path = None
        
        # Check for video file
        if 'video_file' in request.files:
            file = request.files['video_file']
            if allowed_file(file.filename, ALLOWED_VIDEO_EXTENSIONS):
                # Save and convert video to audio first
                filename = secure_filename(file.filename)
                temp_dir = tempfile.mkdtemp()
                file_path = os.path.join(temp_dir, filename)
                file.save(file_path)
                
                # Convert to audio
                audio_path = meeting_assistant.media_converter.convert_mp4_to_mp3(file_path)
                file_path = audio_path
        
        # Check for audio file
        elif 'audio_file' in request.files:
            file = request.files['audio_file']
            if allowed_file(file.filename, ALLOWED_AUDIO_EXTENSIONS):
                filename = secure_filename(file.filename)
                temp_dir = tempfile.mkdtemp()
                file_path = os.path.join(temp_dir, filename)
                file.save(file_path)
        
        if not file_path:
            return jsonify({'error': 'No valid audio or video file provided'}), 400
        
        # Transcribe the audio
        result = meeting_assistant.transcription_service.transcribe_audio(file_path)
        
        # Clean up temporary files
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
        
        return jsonify({
            'success': True,
            'transcript': result['text'],
            'language': result.get('language'),
            'duration': result.get('duration'),
            'output_file': result['output_file']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<path:filename>')
def download_file(filename):
    """Download generated files."""
    try:
        file_path = Config.OUTPUT_FOLDER / filename
        if file_path.exists():
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/audio/<path:filename>')
def serve_audio(filename):
    """Serve audio files for inline playback."""
    try:
        # Check if it's a temp file
        if filename.startswith('temp/'):
            file_path = Config.TEMP_FOLDER / filename[5:]  # Remove 'temp/' prefix and use Config.TEMP_FOLDER
        else:
            file_path = Config.OUTPUT_FOLDER / filename
            
        if file_path.exists():
            # Determine MIME type based on file extension
            extension = Path(filename).suffix.lower()
            mime_type = 'audio/wav' if extension == '.wav' else 'audio/mpeg'
            return send_file(file_path, mimetype=mime_type, as_attachment=False)
        else:
            return jsonify({'error': 'Audio file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/supported-formats', methods=['GET'])
def supported_formats():
    """Get supported file formats."""
    return jsonify({
        'video_formats': list(ALLOWED_VIDEO_EXTENSIONS),
        'audio_formats': list(ALLOWED_AUDIO_EXTENSIONS)
    })

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 500MB'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

@app.route('/chat/start', methods=['POST'])
def start_chat_session():
    """Start a new chat session with transcript context."""
    try:
        data = request.get_json()
        
        if not data or 'transcript' not in data:
            return jsonify({'error': 'No transcript provided'}), 400
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Initialize conversation memory
        memory = ConversationMemory(max_messages=30)  # Store up to 30 messages
        
        # Store session data with memory
        chat_sessions[session_id] = {
            'transcript': data['transcript'],
            'created_at': datetime.now().isoformat(),
            'memory': memory,
            'messages': []  # Keep for backward compatibility
        }
        
        print(f"✅ Created new chat session: {session_id}")
        print(f"📝 Session has transcript of length: {len(data['transcript'])}")
        print(f"🧠 Initialized conversation memory with max {memory.max_messages} messages")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Chat session started. You can now ask questions about the meeting.'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat/<session_id>/message', methods=['POST'])
def send_chat_message(session_id):
    """Send a message in an active chat session."""
    try:
        if session_id not in chat_sessions:
            return jsonify({'error': 'Invalid or expired session'}), 404
        
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        user_message = data['message']
        session_data = chat_sessions[session_id]
        transcript = session_data['transcript']
        memory = session_data['memory']
        
        # Add user message to memory
        memory.add_user_message(user_message)
        
        # Get conversation history for context
        conversation_history = memory.get_recent_context(num_messages=10)
        
        # Create enhanced context-aware prompt with conversation history
        context_prompt = f"""
        You are a helpful AI assistant with access to a meeting transcript and the ongoing conversation history.
        
        **Instructions:**
        - If the user's question is related to the meeting, provide detailed answers based on the meeting content
        - If the question is general, answer as a knowledgeable AI assistant
        - Use the conversation history to maintain context and provide coherent responses
        - Reference previous parts of our conversation when relevant
        
        **Meeting Transcript:**
        {transcript}
        
        **Recent Conversation History:**
        {conversation_history}
        
        **Current User Message:** {user_message}
        
        Please provide a helpful response that takes into account both the meeting content and our conversation history:
        """
        
        print(f"🔄 Processing message for session {session_id}")
        print(f"📝 User message: {user_message[:100]}...")
        print(f"🧠 Using {len(memory.messages)} messages from conversation history")
        
        # Get response from Gemini
        bot_response = meeting_assistant.summarization_service._gpt(context_prompt)
        
        # Add bot response to memory
        memory.add_ai_message(bot_response)
        
        # Store conversation in old format for backward compatibility
        session_data['messages'].append({
            'user': user_message,
            'bot': bot_response,
            'timestamp': datetime.now().isoformat()
        })
        
        print(f"✅ Generated response for session {session_id}")
        print(f"🧠 Memory now contains {len(memory.messages)} total messages")
        
        return jsonify({
            'success': True,
            'response': bot_response,
            'timestamp': datetime.now().isoformat(),
            'conversation_length': len(memory.messages)
        })
        
    except Exception as e:
        print(f"❌ Error in send_chat_message: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat/<session_id>/generate-minutes', methods=['POST'])
def generate_meeting_minutes(session_id):
    """Generate PDF meeting minutes for the session."""
    try:
        print(f"🔄 PDF generation requested for session: {session_id}")
        print(f"🔄 Available sessions: {list(chat_sessions.keys())}")
        
        if session_id not in chat_sessions:
            print(f"❌ Session {session_id} not found in active sessions")
            return jsonify({'error': 'Invalid or expired session'}), 404
        
        data = request.get_json()
        transcript = chat_sessions[session_id]['transcript']
        
        # Get meeting details from request
        meeting_title = data.get('meeting_title', 'Meeting Minutes')
        meeting_date = data.get('meeting_date', datetime.now().strftime('%Y-%m-%d'))
        company_name = data.get('company_name', 'Company')
        
        # Generate summary using existing service
        print(f"🔄 Generating summary for session {session_id}...")
        summary = meeting_assistant.summarization_service.generate_meeting_summary(transcript)
        print(f"✅ Summary generated with {len(summary)} sections")
        
        # Generate PDF
        print(f"🔄 Creating PDF with title: {meeting_title}")
        pdf_result = meeting_assistant.pdf_service.create_meeting_minutes_pdf(
            summary=summary,
            meeting_title=meeting_title,
            meeting_date=meeting_date,
            company_name=company_name
        )
        
        if not pdf_result.get('success'):
            raise Exception(pdf_result.get('error', 'PDF generation failed'))
        
        print(f"✅ PDF created: {pdf_result['pdf_file']}")
        
        return jsonify({
            'success': True,
            'pdf_file': pdf_result['pdf_file'],
            'download_url': f"/download/{Path(pdf_result['pdf_file']).name}"
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat/<session_id>/send-email', methods=['POST'])
def send_meeting_email(session_id):
    """Send meeting minutes via email."""
    try:
        print(f"🔄 Email endpoint called for session: {session_id}")
        print(f"🔄 Available sessions: {list(chat_sessions.keys())}")
        
        if session_id not in chat_sessions:
            print(f"❌ Session {session_id} not found")
            return jsonify({'error': 'Invalid or expired session'}), 404
        
        data = request.get_json()
        print(f"🔄 Received data: {data}")
        
        if not data:
            print(f"❌ No data received")
            return jsonify({'error': 'No data provided'}), 400
            
        if 'recipients' not in data:
            print(f"❌ No recipients provided in data: {data}")
            return jsonify({'error': 'No recipients provided'}), 400
        
        recipients = data['recipients']
        if not recipients or len(recipients) == 0:
            print(f"❌ Empty recipients list: {recipients}")
            return jsonify({'error': 'Recipients list is empty'}), 400
        
        transcript = chat_sessions[session_id]['transcript']
        
        # Get meeting details
        meeting_title = data.get('meeting_title', 'Meeting Minutes')
        meeting_date = data.get('meeting_date', datetime.now().strftime('%Y-%m-%d'))
        company_name = data.get('company_name', 'Company')
        custom_message = data.get('custom_message', '')
        
        print(f"🔄 Processing email with:")
        print(f"   - Recipients: {recipients}")
        print(f"   - Title: {meeting_title}")
        print(f"   - Date: {meeting_date}")
        print(f"   - Company: {company_name}")
        
        # Generate summary and PDF
        print(f"🔄 Generating summary for email...")
        summary = meeting_assistant.summarization_service.generate_meeting_summary(transcript)
        
        print(f"🔄 Creating PDF for email...")
        pdf_result = meeting_assistant.pdf_service.create_meeting_minutes_pdf(
            summary=summary,
            meeting_title=meeting_title,
            meeting_date=meeting_date,
            company_name=company_name
        )
        
        if not pdf_result.get('success'):
            error_msg = pdf_result.get('error', 'PDF generation failed')
            print(f"❌ PDF generation failed: {error_msg}")
            return jsonify({'error': f'PDF generation failed: {error_msg}'}), 500
        
        print(f"✅ PDF created: {pdf_result['pdf_file']}")
        
        # Send emails
        print(f"🔄 Sending emails to {len(recipients)} recipients...")
        email_result = meeting_assistant.email_service.send_meeting_minutes(
            recipients=recipients,
            pdf_file_path=pdf_result['pdf_file'],
            meeting_title=meeting_title,
            meeting_date=meeting_date,
            custom_message=custom_message
        )
        
        print(f"� Email result: {email_result}")
        
        if email_result.get('success'):
            return jsonify({
                'success': True,
                'data': {
                    'message': f"Email sent successfully to {len(recipients)} recipients",
                    'email_result': email_result,
                    'pdf_file': pdf_result['pdf_file']
                },
                'message': f"Email sent successfully to {len(recipients)} recipients"
            })
        else:
            error_msg = email_result.get('error', 'Unknown email error')
            print(f"❌ Email sending failed: {error_msg}")
            return jsonify({'success': False, 'error': f'Email sending failed: {error_msg}'}), 500
        
    except Exception as e:
        print(f"❌ Error in send_meeting_email: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/chat/<session_id>/tts', methods=['POST'])
def generate_tts(session_id):
    """Generate TTS audio for given text."""
    try:
        if session_id not in chat_sessions:
            return jsonify({'error': 'Invalid or expired session'}), 404
        
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
            
        text = data['text'].strip()
        if not text:
            return jsonify({'error': 'Text cannot be empty'}), 400
        
        # Generate TTS audio
        audio_file = tts_service.generate_speech(text)
        
        # Convert to relative path for audio serving
        audio_filename = Path(audio_file).name
        
        return jsonify({
            'success': True,
            'audio_url': f'/audio/temp/{audio_filename}',
            'message': 'TTS audio generated successfully'
        })
        
    except Exception as e:
        print(f"TTS Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat/<session_id>/history', methods=['GET'])
def get_chat_history(session_id):
    """Get chat history for a session."""
    try:
        if session_id not in chat_sessions:
            return jsonify({'error': 'Invalid or expired session'}), 404
        
        session_data = chat_sessions[session_id]
        memory = session_data.get('memory')
        
        # Return both old format and new memory format
        response_data = {
            'success': True,
            'created_at': session_data['created_at'],
            'messages': session_data['messages'],  # Backward compatibility
        }
        
        # Add memory-based conversation history if available
        if memory:
            response_data.update({
                'conversation_memory': {
                    'total_messages': len(memory.messages),
                    'max_messages': memory.max_messages,
                    'conversation_history': memory.get_conversation_history(),
                    'recent_context': memory.get_recent_context(5)
                }
            })
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/debug/test-tts', methods=['POST'])
def debug_test_tts():
    """Debug TTS endpoint for testing."""
    try:
        data = request.get_json()
        text = data.get('text', 'This is a test message.')
        
        print(f"🧪 Debug TTS request for text: {text}")
        
        # Generate TTS audio
        audio_file = tts_service.generate_speech(text)
        print(f"🔊 Generated audio file: {audio_file}")
        
        # Convert to relative path for audio serving
        audio_filename = Path(audio_file).name
        audio_url = f'/audio/temp/{audio_filename}'
        
        print(f"📍 Audio URL: {audio_url}")
        print(f"📁 Audio file exists: {Path(audio_file).exists()}")
        print(f"📏 Audio file size: {Path(audio_file).stat().st_size if Path(audio_file).exists() else 'N/A'} bytes")
        
        return jsonify({
            'success': True,
            'audio_url': audio_url,
            'audio_file_path': str(audio_file),
            'audio_filename': audio_filename,
            'file_exists': Path(audio_file).exists(),
            'message': 'Debug TTS audio generated successfully'
        })
        
    except Exception as e:
        print(f"❌ Debug TTS Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/debug/sessions', methods=['GET'])
def debug_sessions():
    """Debug endpoint to check active sessions."""
    sessions_detail = {}
    for k, v in chat_sessions.items():
        memory = v.get('memory')
        detail = {
            'created_at': v['created_at'], 
            'transcript_length': len(v['transcript']), 
            'message_count': len(v['messages'])
        }
        
        # Add memory information if available
        if memory:
            detail.update({
                'memory_messages': len(memory.messages),
                'memory_max': memory.max_messages,
                'has_conversation_memory': True
            })
        else:
            detail['has_conversation_memory'] = False
            
        sessions_detail[k] = detail
    
    return jsonify({
        'active_sessions': list(chat_sessions.keys()),
        'session_count': len(chat_sessions),
        'sessions_detail': sessions_detail
    })

@app.route('/debug/create-test-session', methods=['POST'])
def create_test_session():
    """Create a test session with the existing test transcript."""
    try:
        test_transcript_path = Path(Config.OUTPUT_FOLDER) / 'test_transcript.txt'
        
        if not test_transcript_path.exists():
            return jsonify({'error': 'Test transcript not found'}), 404
            
        with open(test_transcript_path, 'r', encoding='utf-8') as f:
            transcript = f.read()
        
        # Create a new chat session with the test transcript and memory
        session_id = str(uuid.uuid4())
        memory = ConversationMemory(max_messages=25)
        
        chat_sessions[session_id] = {
            'transcript': transcript,
            'memory': memory,
            'messages': [],
            'created_at': datetime.now().isoformat()
        }
        
        print(f"✅ Created debug test session: {session_id}")
        print(f"🧠 Initialized with conversation memory (max {memory.max_messages} messages)")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'transcript': transcript,
            'memory_info': {
                'max_messages': memory.max_messages,
                'current_messages': len(memory.messages)
            },
            'message': 'Debug test session created successfully with conversation memory'
        })
        
    except Exception as e:
        print(f"Debug test session error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/debug/test-email', methods=['POST'])
def debug_test_email():
    """Debug endpoint to test email configuration."""
    try:
        data = request.get_json()
        test_recipients = data.get('recipients', ['test@example.com'])
        
        print(f"🧪 Debug email test for recipients: {test_recipients}")
        
        # Test email service connection first
        print(f"🔄 Testing email connection...")
        connection_test = meeting_assistant.email_service.test_connection()
        print(f"📧 Connection test result: {connection_test}")
        
        if not connection_test:
            return jsonify({
                'success': False,
                'error': 'Email service connection failed',
                'message': 'Check email configuration in config.py'
            }), 500
        
        # Try to send a test email
        test_pdf_path = Path(Config.OUTPUT_FOLDER) / 'test_transcript.txt'  # Use transcript as test file
        if not test_pdf_path.exists():
            return jsonify({
                'success': False,
                'error': 'Test file not found',
                'message': 'No test file available for email test'
            }), 404
        
        print(f"🔄 Sending test email...")
        email_result = meeting_assistant.email_service.send_meeting_minutes(
            recipients=test_recipients,
            pdf_file_path=str(test_pdf_path),
            meeting_title="Test Email",
            meeting_date="2025-01-15",
            custom_message="This is a test email from ConverSync."
        )
        
        print(f"📧 Test email result: {email_result}")
        
        return jsonify({
            'success': email_result.get('success', False),
            'message': email_result.get('message', 'Unknown result'),
            'email_result': email_result,
            'connection_test': connection_test
        })
        
    except Exception as e:
        print(f"❌ Debug email test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/chat/<session_id>/memory', methods=['GET'])
def get_conversation_memory(session_id):
    """Get detailed conversation memory for a session."""
    try:
        if session_id not in chat_sessions:
            return jsonify({'error': 'Invalid or expired session'}), 404
        
        session_data = chat_sessions[session_id]
        memory = session_data.get('memory')
        
        if not memory:
            return jsonify({'error': 'No conversation memory found for this session'}), 404
        
        return jsonify({
            'success': True,
            'memory_info': {
                'total_messages': len(memory.messages),
                'max_messages': memory.max_messages,
                'conversation_history': memory.get_conversation_history(),
                'recent_context': memory.get_recent_context(10),
                'messages': memory.messages
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat/<session_id>/memory/clear', methods=['POST'])
def clear_conversation_memory(session_id):
    """Clear conversation memory for a session."""
    try:
        if session_id not in chat_sessions:
            return jsonify({'error': 'Invalid or expired session'}), 404
        
        session_data = chat_sessions[session_id]
        memory = session_data.get('memory')
        
        if not memory:
            return jsonify({'error': 'No conversation memory found for this session'}), 404
        
        messages_before = len(memory.messages)
        memory.clear()
        
        print(f"🧠 Cleared conversation memory for session {session_id}")
        print(f"📝 Removed {messages_before} messages from memory")
        
        return jsonify({
            'success': True,
            'message': f'Conversation memory cleared. Removed {messages_before} messages.',
            'messages_removed': messages_before
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat/<session_id>/memory/summary', methods=['GET'])
def get_memory_summary(session_id):
    """Get a summary of the conversation memory."""
    try:
        if session_id not in chat_sessions:
            return jsonify({'error': 'Invalid or expired session'}), 404
        
        session_data = chat_sessions[session_id]
        memory = session_data.get('memory')
        
        if not memory:
            return jsonify({'error': 'No conversation memory found for this session'}), 404
        
        # Count message types
        user_messages = sum(1 for msg in memory.messages if msg['type'] == 'user')
        ai_messages = sum(1 for msg in memory.messages if msg['type'] == 'ai')
        
        return jsonify({
            'success': True,
            'summary': {
                'total_messages': len(memory.messages),
                'user_messages': user_messages,
                'ai_messages': ai_messages,
                'max_capacity': memory.max_messages,
                'memory_usage_percent': round((len(memory.messages) / memory.max_messages) * 100, 1),
                'session_created': session_data['created_at'],
                'has_recent_activity': len(memory.messages) > 0
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def main():
    """Main entry point for the Flask application."""
    # Ensure directories exist
    Config.ensure_directories()
    
    print("🚀 Starting ConverSync Meeting Assistant API...")
    print(f"📍 API will be available at: http://localhost:5000")
    print("📖 API Documentation: See README.md for endpoint details")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
