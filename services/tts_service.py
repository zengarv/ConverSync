import os
import tempfile
from pathlib import Path
from groq import Groq
from config import Config

class TTSService:
    """Text-to-Speech service using Groq API."""
    
    def __init__(self):
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = "playai-tts"
        self.voice = "Celeste-PlayAI"
        self.response_format = "wav"
        
    def generate_speech(self, text: str, output_file: str = None) -> str:
        """
        Generate speech from text using Groq TTS.
        
        Args:
            text (str): Text to convert to speech
            output_file (str, optional): Output file path. If None, generates temp file.
            
        Returns:
            str: Path to the generated audio file
        """
        try:
            if not text or text.strip() == "":
                raise ValueError("Text cannot be empty")
                
            # Generate output file path if not provided
            if output_file is None:
                temp_dir = Path(Config.TEMP_FOLDER)
                temp_dir.mkdir(exist_ok=True)
                output_file = temp_dir / f"tts_{hash(text) % 1000000}.wav"
            
            # Create TTS request
            response = self.client.audio.speech.create(
                model=self.model,
                voice=self.voice,
                input=text,
                response_format=self.response_format
            )
            
            # Write response to file
            response.write_to_file(str(output_file))
            
            return str(output_file)
            
        except Exception as e:
            raise Exception(f"TTS generation failed: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if TTS service is available."""
        return bool(Config.GROQ_API_KEY)
