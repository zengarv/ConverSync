import os
from pathlib import Path
from groq import Groq
from config import Config

class TranscriptionService:
    """Service for transcribing audio files using Groq API."""
    
    def __init__(self):
        Config.validate_config()
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        Config.ensure_directories()
    
    def transcribe_audio(self, audio_file_path: str, output_file_path: str = None) -> dict:
        """
        Transcribe an audio file to text.
        
        Args:
            audio_file_path (str): Path to the audio file.
            output_file_path (str, optional): Path to save the transcription text file.
                                            If not provided, will be generated automatically.
        
        Returns:
            dict: Transcription result with text and metadata.
            
        Raises:
            FileNotFoundError: If the audio file doesn't exist.
            Exception: If transcription fails.
        """
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found at '{audio_file_path}'")
        
        try:
            with open(audio_file_path, "rb") as file:
                transcription = self.client.audio.transcriptions.create(
                    file=(os.path.basename(audio_file_path), file.read()),
                    model=Config.GROQ_MODEL,
                    response_format="verbose_json",
                )
            
            # Generate output path if not provided
            if output_file_path is None:
                input_path = Path(audio_file_path)
                output_file_path = str(Config.OUTPUT_FOLDER / f"{input_path.stem}_transcription.txt")
            
            # Save transcription to file
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(transcription.text)
            
            print(f"Transcription saved to '{output_file_path}'")
            
            return {
                'text': transcription.text,
                'language': getattr(transcription, 'language', None),
                'duration': getattr(transcription, 'duration', None),
                'output_file': output_file_path,
                'segments': getattr(transcription, 'segments', None)
            }
            
        except Exception as e:
            raise Exception(f"An error occurred during transcription: {e}")
    
    def transcribe_from_file(self, file_path: str) -> str:
        """
        Simple transcription that returns only the text.
        
        Args:
            file_path (str): Path to the audio file.
            
        Returns:
            str: Transcribed text.
        """
        result = self.transcribe_audio(file_path)
        return result['text']
    
    def batch_transcribe(self, audio_files: list) -> list:
        """
        Transcribe multiple audio files.
        
        Args:
            audio_files (list): List of audio file paths.
            
        Returns:
            list: List of transcription results.
        """
        results = []
        for audio_file in audio_files:
            try:
                result = self.transcribe_audio(audio_file)
                results.append({
                    'file': audio_file,
                    'success': True,
                    'result': result
                })
            except Exception as e:
                results.append({
                    'file': audio_file,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def get_supported_formats(self) -> list:
        """
        Get list of supported audio formats.
        
        Returns:
            list: Supported audio formats.
        """
        return ['mp3', 'wav', 'flac', 'm4a', 'ogg', 'webm']
