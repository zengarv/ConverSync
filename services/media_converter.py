import os
import sys
from pathlib import Path
try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    try:
        from moviepy import VideoFileClip
        MOVIEPY_AVAILABLE = True
    except ImportError:
        VideoFileClip = None
        MOVIEPY_AVAILABLE = False
        print("Warning: MoviePy not available. Video conversion features will be disabled.")

from config import Config

class MediaConverter:
    """Service for converting video files to audio files."""
    
    def __init__(self):
        Config.ensure_directories()
    
    def convert_mp4_to_mp3(self, mp4_file_path: str, mp3_file_path: str = None) -> str:
        """
        Converts an MP4 video file to an MP3 audio file.

        Args:
            mp4_file_path (str): The full path to the input MP4 video file.
            mp3_file_path (str, optional): The full path where the output MP3 audio file will be saved.
                                         If not provided, will be generated automatically.

        Returns:
            str: Path to the converted MP3 file.
            
        Raises:
            FileNotFoundError: If the input MP4 file doesn't exist.
            Exception: If conversion fails.
        """
        if not MOVIEPY_AVAILABLE:
            raise Exception("MoviePy not available. Cannot convert video files.")
            
        if not os.path.exists(mp4_file_path):
            raise FileNotFoundError(f"MP4 file not found at '{mp4_file_path}'")

        # Generate output path if not provided
        if mp3_file_path is None:
            input_path = Path(mp4_file_path)
            mp3_file_path = str(Config.OUTPUT_FOLDER / f"{input_path.stem}.mp3")

        try:
            # Load the video clip
            video_clip = VideoFileClip(mp4_file_path)

            # Extract the audio
            audio_clip = video_clip.audio

            # Write the audio to an MP3 file with error handling for different MoviePy versions
            try:
                # Try with verbose parameter first (older versions)
                audio_clip.write_audiofile(mp3_file_path, verbose=False, logger=None)
            except TypeError:
                # If that fails, try without verbose parameter (newer versions)
                try:
                    audio_clip.write_audiofile(mp3_file_path, logger=None)
                except TypeError:
                    # If that also fails, use basic call
                    audio_clip.write_audiofile(mp3_file_path)

            # Close the clips
            audio_clip.close()
            video_clip.close()

            print(f"Successfully converted '{mp4_file_path}' to '{mp3_file_path}'")
            return mp3_file_path

        except Exception as e:
            raise Exception(f"An error occurred during conversion: {e}")
    
    def convert_video_to_audio(self, video_path: str, output_format: str = "mp3") -> str:
        """
        Generic method to convert video to audio in different formats.
        
        Args:
            video_path (str): Path to the input video file.
            output_format (str): Output audio format (mp3, wav, etc.).
            
        Returns:
            str: Path to the converted audio file.
        """
        if not MOVIEPY_AVAILABLE:
            raise Exception("MoviePy not available. Cannot convert video files.")
            
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found at '{video_path}'")
        
        input_path = Path(video_path)
        output_path = str(Config.OUTPUT_FOLDER / f"{input_path.stem}.{output_format}")
        
        try:
            video_clip = VideoFileClip(video_path)
            audio_clip = video_clip.audio
            
            # Handle different MoviePy versions
            try:
                audio_clip.write_audiofile(output_path, verbose=False, logger=None)
            except TypeError:
                try:
                    audio_clip.write_audiofile(output_path, logger=None)
                except TypeError:
                    audio_clip.write_audiofile(output_path)
            
            audio_clip.close()
            video_clip.close()
            
            return output_path
            
        except Exception as e:
            raise Exception(f"An error occurred during conversion: {e}")
    
    def get_video_info(self, video_path: str) -> dict:
        """
        Get information about a video file.
        
        Args:
            video_path (str): Path to the video file.
            
        Returns:
            dict: Video information including duration, fps, size, etc.
        """
        if not MOVIEPY_AVAILABLE:
            raise Exception("MoviePy not available. Cannot get video info.")
            
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found at '{video_path}'")
        
        try:
            video_clip = VideoFileClip(video_path)
            info = {
                'duration': video_clip.duration,
                'fps': video_clip.fps,
                'size': video_clip.size,
                'filename': Path(video_path).name,
                'filesize': os.path.getsize(video_path)
            }
            video_clip.close()
            return info
            
        except Exception as e:
            raise Exception(f"An error occurred while getting video info: {e}")
    
    def is_available(self) -> bool:
        """Check if MoviePy is available for video processing."""
        return MOVIEPY_AVAILABLE
