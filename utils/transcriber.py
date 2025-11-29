from faster_whisper import WhisperModel
import os

# Global model cache to avoid reloading
_model_cache = None

def get_whisper_model():
    """Get or create cached Whisper model"""
    global _model_cache
    if _model_cache is None:
        # Use "tiny" model for faster processing and lower memory usage on free tier
        # Options: tiny, base, small, medium, large
        model_size = os.environ.get('WHISPER_MODEL', 'tiny')
        _model_cache = WhisperModel(model_size, device="cpu", compute_type="int8")
    return _model_cache

def transcribe_audio(audio_path):
    """
    Transcribe audio file using faster-whisper model
    
    Args:
        audio_path: Path to audio file to transcribe
        
    Returns:
        tuple: (detected_language, list_of_segments)
    """
    try:
        # Get cached model
        model = get_whisper_model()
        
        # Transcribe the audio with optimized settings for speed
        segments, info = model.transcribe(
            audio_path, 
            beam_size=1,  # Faster, less accurate
            best_of=1,
            temperature=0
        )
        
        # Get detected language
        detected_language = info.language
        
        # Convert generator to list
        segments_list = list(segments)
        
        return detected_language, segments_list
        
    except Exception as e:
        raise Exception(f"Error during transcription: {str(e)}")

def format_segment_info(segment):
    """
    Format segment information for display
    
    Args:
        segment: Segment object from faster-whisper
        
    Returns:
        str: Formatted segment information
    """
    return f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}"
