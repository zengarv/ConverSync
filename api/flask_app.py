from flask import Flask, request, jsonify, send_file, session, send_from_directory
from werkzeug.utils import secure_filename
import os
from pathlib import Path
import tempfile
import json
from datetime import datetime
import uuid

from api.meeting_assistant import MeetingAssistant
from config import Config

app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.secret_key = 'your-secret-key-change-this'  # Change this in production

# Initialize the meeting assistant
meeting_assistant = MeetingAssistant()

# Store active chat sessions
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
    """Serve the main frontend application."""
    return send_from_directory(app.static_folder, 'app.html')

@app.route('/test', methods=['GET'])
def serve_test_page():
    """Serve the test page."""
    return send_from_directory(app.static_folder, 'test.html')

@app.route('/api', methods=['GET'])
def api_info():
    """API information endpoint."""
    return jsonify({
        'message': 'ConverSync Meeting Assistant API',
        'version': '1.0.0',
        'frontend_url': 'http://localhost:5000/',
        'test_url': 'http://localhost:5000/test',
        'endpoints': {
            'health': '/health',
            'transcribe': '/transcribe-only',
            'chat_start': '/chat/start',
            'chat_message': '/chat/{session_id}/message',
            'generate_pdf': '/chat/{session_id}/generate-minutes',
            'send_email': '/chat/{session_id}/send-email',
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
        
        # Store session data
        chat_sessions[session_id] = {
            'transcript': data['transcript'],
            'created_at': datetime.now().isoformat(),
            'messages': []
        }
        
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
        transcript = chat_sessions[session_id]['transcript']
        
        # Create context-aware prompt
        context_prompt = f"""
        You are a helpful meeting assistant. You have access to the transcript of a recent meeting.
        Please answer the user's question based on the meeting content.
        
        Meeting Transcript:
        {transcript}
        
        User Question: {user_message}
        
        Please provide a helpful and accurate response based on the meeting content:
        """
        
        # Get response from Gemini
        bot_response = meeting_assistant.summarization_service._gpt(context_prompt)
        
        # Store conversation
        chat_sessions[session_id]['messages'].append({
            'user': user_message,
            'bot': bot_response,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'success': True,
            'response': bot_response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat/<session_id>/generate-minutes', methods=['POST'])
def generate_meeting_minutes(session_id):
    """Generate PDF meeting minutes for the session."""
    try:
        if session_id not in chat_sessions:
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
        
        if not data or 'recipients' not in data:
            print(f"❌ No recipients provided in data: {data}")
            return jsonify({'error': 'No recipients provided'}), 400
        
        transcript = chat_sessions[session_id]['transcript']
        recipients = data['recipients']
        
        # Get meeting details
        meeting_title = data.get('meeting_title', 'Meeting Minutes')
        meeting_date = data.get('meeting_date', datetime.now().strftime('%Y-%m-%d'))
        company_name = data.get('company_name', 'Company')
        custom_message = data.get('custom_message', '')
        
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
            raise Exception(pdf_result.get('error', 'PDF generation failed'))
        
        # Send emails
        print(f"🔄 Sending emails to {len(recipients)} recipients...")
        email_result = meeting_assistant.email_service.send_meeting_minutes(
            recipients=recipients,
            pdf_file_path=pdf_result['pdf_file'],
            meeting_title=meeting_title,
            meeting_date=meeting_date,
            custom_message=custom_message
        )
        
        print(f"🔄 Email result: {email_result}")
        
        return jsonify({
            'success': True,
            'email_result': email_result,
            'pdf_file': pdf_result['pdf_file']
        })
        
    except Exception as e:
        print(f"❌ Error in send_meeting_email: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/chat/<session_id>/history', methods=['GET'])
def get_chat_history(session_id):
    """Get chat history for a session."""
    try:
        if session_id not in chat_sessions:
            return jsonify({'error': 'Invalid or expired session'}), 404
        
        return jsonify({
            'success': True,
            'messages': chat_sessions[session_id]['messages'],
            'created_at': chat_sessions[session_id]['created_at']
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
