"""
Speech-to-Text Module using OpenAI Whisper
"""
import whisper
import torch
import numpy as np
from typing import Optional
import config


class SpeechToText:
    """
    Handles speech-to-text conversion using Whisper model
    """
    
    def __init__(self, model_name: str = None):
        """
        Initialize Whisper model
        
        Args:
            model_name: Size of Whisper model (tiny, base, small, medium, large)
        """
        self.model_name = model_name or config.WHISPER_MODEL
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading Whisper model '{self.model_name}' on {self.device}...")
        self.model = whisper.load_model(self.model_name, device=self.device)
        print("Whisper model loaded successfully!")
    
    def transcribe_audio(self, audio_path: str, language: str = "en") -> str:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file
            language: Language code (default: English)
        
        Returns:
            Transcribed text
        """
        try:
            # Transcribe audio
            result = self.model.transcribe(
                audio_path,
                language=language,
                fp16=(self.device == "cuda")
            )
            
            # Extract text
            text = result["text"].strip()
            
            if not text:
                return "No speech detected. Please try again."
            
            return text
        
        except Exception as e:
            print(f"Error during transcription: {e}")
            return f"Error: Could not transcribe audio. {str(e)}"
    
    def transcribe_array(self, audio_array: np.ndarray, sample_rate: int = 16000) -> str:
        """
        Transcribe audio from numpy array

        Args:
            audio_array: Audio data as numpy array
            sample_rate: Sample rate of audio

        Returns:
            Transcribed text
        """
        try:
            # Ensure audio is float32
            if audio_array.dtype != np.float32:
                audio_array = audio_array.astype(np.float32)

            # Handle stereo audio - convert to mono
            if len(audio_array.shape) > 1:
                audio_array = audio_array.mean(axis=1)

            # Normalize audio to [-1, 1] range
            max_val = np.abs(audio_array).max()
            if max_val > 0:
                audio_array = audio_array / max_val

            # Resample to 16kHz if needed (Whisper expects 16kHz)
            if sample_rate != 16000:
                import scipy.signal as signal
                num_samples = int(len(audio_array) * 16000 / sample_rate)
                audio_array = signal.resample(audio_array, num_samples)

            print(f"[DEBUG] Audio shape: {audio_array.shape}, dtype: {audio_array.dtype}, range: [{audio_array.min():.3f}, {audio_array.max():.3f}]")

            # Transcribe with better settings
            result = self.model.transcribe(
                audio_array,
                language="en",  # Force English
                fp16=(self.device == "cuda"),
                task="transcribe",  # Not translate
                verbose=False
            )

            text = result["text"].strip()
            print(f"[DEBUG] Whisper transcription: '{text}'")

            if not text:
                return "No speech detected. Please try again."

            return text

        except Exception as e:
            print(f"Error during transcription: {e}")
            import traceback
            traceback.print_exc()
            return f"Error: Could not transcribe audio. {str(e)}"


# Global instance (lazy loading)
_stt_instance: Optional[SpeechToText] = None


def get_stt_instance() -> SpeechToText:
    """
    Get or create global SpeechToText instance
    """
    global _stt_instance
    if _stt_instance is None:
        _stt_instance = SpeechToText()
    return _stt_instance
