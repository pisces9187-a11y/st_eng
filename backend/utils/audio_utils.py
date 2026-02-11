"""
Enhanced Audio Utilities for English Learning Platform

Features:
- Audio duration calculation
- Audio optimization and compression
- Format conversion
- Metadata extraction
- Batch processing
- Edge TTS integration helpers
"""

import os
import logging
import hashlib
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

# Optional imports
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    logger.warning("pydub not installed. Audio optimization features disabled.")

try:
    from mutagen.mp3 import MP3
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False
    logger.warning("mutagen not installed. Audio duration calculation limited.")


# =========================================================================
# AUDIO FILE INFORMATION
# =========================================================================

def get_audio_duration(file_path: str) -> float:
    """
    Get audio file duration in seconds.
    
    Args:
        file_path: Path to audio file
    
    Returns:
        Duration in seconds (float), 0.0 if error
    
    Example:
        >>> duration = get_audio_duration("audio.mp3")
        >>> print(f"Duration: {duration:.2f}s")
    """
    if not MUTAGEN_AVAILABLE:
        logger.warning("mutagen not available, returning 0 duration")
        return 0.0
    
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return 0.0
    
    try:
        audio = MP3(file_path)
        return audio.info.length
    except Exception as e:
        logger.error(f"Failed to get duration for {file_path}: {e}")
        return 0.0


def get_audio_metadata(file_path: str) -> Dict:
    """
    Extract audio file metadata.
    
    Args:
        file_path: Path to audio file
    
    Returns:
        Dict with metadata (duration, bitrate, sample_rate, etc.)
    """
    metadata = {
        'duration': 0.0,
        'bitrate': 0,
        'sample_rate': 0,
        'channels': 0,
        'file_size': 0,
        'format': Path(file_path).suffix.lstrip('.')
    }
    
    if not os.path.exists(file_path):
        return metadata
    
    # File size
    metadata['file_size'] = os.path.getsize(file_path)
    
    # Duration
    if MUTAGEN_AVAILABLE:
        try:
            audio = MP3(file_path)
            metadata['duration'] = audio.info.length
            metadata['bitrate'] = audio.info.bitrate
            metadata['sample_rate'] = audio.info.sample_rate
            metadata['channels'] = audio.info.channels
        except Exception as e:
            logger.warning(f"Failed to extract metadata: {e}")
    
    return metadata


def calculate_audio_hash(file_path: str) -> str:
    """
    Calculate MD5 hash of audio file for deduplication.
    
    Args:
        file_path: Path to audio file
    
    Returns:
        MD5 hash string
    """
    if not os.path.exists(file_path):
        return ""
    
    try:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        logger.error(f"Failed to calculate hash: {e}")
        return ""


# =========================================================================
# AUDIO OPTIMIZATION
# =========================================================================

def optimize_audio(
    input_path: str,
    output_path: Optional[str] = None,
    bitrate: str = '128k',
    sample_rate: int = 44100,
    mono: bool = True
) -> str:
    """
    Optimize audio file (compress, normalize).
    
    Args:
        input_path: Path to input audio
        output_path: Path to save optimized audio (default: overwrite)
        bitrate: Target bitrate (e.g., '128k', '192k')
        sample_rate: Target sample rate (e.g., 44100, 48000)
        mono: Convert to mono (phonemes don't need stereo)
    
    Returns:
        Path to optimized audio file
    
    Example:
        >>> optimized = optimize_audio("input.mp3", bitrate="96k", mono=True)
        >>> print(f"Optimized: {optimized}")
    """
    if not PYDUB_AVAILABLE:
        logger.warning("pydub not available, returning original file")
        return input_path
    
    if not os.path.exists(input_path):
        logger.error(f"Input file not found: {input_path}")
        return input_path
    
    if not output_path:
        output_path = input_path
    
    try:
        # Load audio
        audio = AudioSegment.from_file(input_path)
        
        # Convert to mono if requested
        if mono and audio.channels > 1:
            audio = audio.set_channels(1)
            logger.info(f"Converted to mono: {input_path}")
        
        # Normalize loudness
        audio = audio.normalize()
        
        # Export with optimization
        export_params = [
            "-ar", str(sample_rate),  # Sample rate
        ]
        
        if mono:
            export_params.extend(["-ac", "1"])  # Mono
        
        audio.export(
            output_path,
            format='mp3',
            bitrate=bitrate,
            parameters=export_params
        )
        
        # Log file size reduction
        if input_path != output_path:
            original_size = os.path.getsize(input_path)
            optimized_size = os.path.getsize(output_path)
            reduction = ((original_size - optimized_size) / original_size) * 100 if original_size > 0 else 0
            
            logger.info(
                f"Audio optimized: {Path(input_path).name} -> {Path(output_path).name} "
                f"({original_size} -> {optimized_size} bytes, {reduction:.1f}% reduction)"
            )
        
        return output_path
        
    except Exception as e:
        logger.error(f"Audio optimization failed: {e}")
        return input_path  # Return original if optimization fails


def batch_optimize_audio(
    input_dir: str,
    output_dir: Optional[str] = None,
    **kwargs
) -> List[str]:
    """
    Batch optimize all audio files in a directory.
    
    Args:
        input_dir: Directory with input audio files
        output_dir: Directory for optimized files (default: same as input)
        **kwargs: Parameters for optimize_audio
    
    Returns:
        List of optimized file paths
    """
    if not os.path.isdir(input_dir):
        logger.error(f"Input directory not found: {input_dir}")
        return []
    
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    optimized_files = []
    audio_extensions = {'.mp3', '.wav', '.ogg', '.m4a', '.flac'}
    
    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        
        if not os.path.isfile(file_path):
            continue
        
        if Path(file_path).suffix.lower() not in audio_extensions:
            continue
        
        # Determine output path
        if output_dir:
            output_path = os.path.join(output_dir, filename)
        else:
            output_path = file_path
        
        # Optimize
        optimized = optimize_audio(file_path, output_path, **kwargs)
        optimized_files.append(optimized)
    
    logger.info(f"Batch optimized {len(optimized_files)} files")
    return optimized_files


# =========================================================================
# AUDIO FORMAT CONVERSION
# =========================================================================

def convert_audio_format(
    input_path: str,
    output_format: str = 'mp3',
    output_path: Optional[str] = None,
    bitrate: str = '192k'
) -> str:
    """
    Convert audio to different format.
    
    Args:
        input_path: Path to input audio
        output_format: Target format ('mp3', 'wav', 'ogg')
        output_path: Path to save converted audio
        bitrate: Target bitrate
    
    Returns:
        Path to converted audio
    
    Example:
        >>> converted = convert_audio_format("audio.wav", "mp3", bitrate="128k")
    """
    if not PYDUB_AVAILABLE:
        logger.warning("pydub not available, returning original file")
        return input_path
    
    if not os.path.exists(input_path):
        logger.error(f"Input file not found: {input_path}")
        return input_path
    
    if not output_path:
        output_path = str(Path(input_path).with_suffix(f'.{output_format}'))
    
    try:
        audio = AudioSegment.from_file(input_path)
        audio.export(output_path, format=output_format, bitrate=bitrate)
        
        logger.info(f"Audio converted: {Path(input_path).name} -> {Path(output_path).name}")
        return output_path
        
    except Exception as e:
        logger.error(f"Audio conversion failed: {e}")
        raise


# =========================================================================
# AUDIO TRIMMING & MANIPULATION
# =========================================================================

def trim_silence(
    input_path: str,
    output_path: Optional[str] = None,
    silence_threshold: int = -40,
    chunk_size: int = 10
) -> str:
    """
    Trim silence from beginning and end of audio.
    
    Args:
        input_path: Path to input audio
        output_path: Path to save trimmed audio
        silence_threshold: Silence threshold in dBFS (default: -40)
        chunk_size: Chunk size in ms for detection (default: 10)
    
    Returns:
        Path to trimmed audio
    """
    if not PYDUB_AVAILABLE:
        logger.warning("pydub not available, returning original file")
        return input_path
    
    if not output_path:
        output_path = input_path
    
    try:
        from pydub.silence import detect_nonsilent
        
        audio = AudioSegment.from_file(input_path)
        
        # Detect non-silent chunks
        nonsilent_ranges = detect_nonsilent(
            audio,
            min_silence_len=chunk_size,
            silence_thresh=silence_threshold
        )
        
        if not nonsilent_ranges:
            logger.warning(f"No non-silent audio detected in {input_path}")
            return input_path
        
        # Get first and last non-silent positions
        start = nonsilent_ranges[0][0]
        end = nonsilent_ranges[-1][1]
        
        # Trim audio
        trimmed = audio[start:end]
        trimmed.export(output_path, format='mp3')
        
        logger.info(f"Silence trimmed: {input_path} ({start}ms - {end}ms)")
        return output_path
        
    except Exception as e:
        logger.error(f"Trim silence failed: {e}")
        return input_path


def add_silence_padding(
    input_path: str,
    output_path: Optional[str] = None,
    padding_start: int = 100,
    padding_end: int = 100
) -> str:
    """
    Add silence padding to beginning and end of audio.
    
    Args:
        input_path: Path to input audio
        output_path: Path to save padded audio
        padding_start: Padding at start in ms (default: 100)
        padding_end: Padding at end in ms (default: 100)
    
    Returns:
        Path to padded audio
    """
    if not PYDUB_AVAILABLE:
        logger.warning("pydub not available, returning original file")
        return input_path
    
    if not output_path:
        output_path = input_path
    
    try:
        audio = AudioSegment.from_file(input_path)
        
        # Create silence
        silence_start = AudioSegment.silent(duration=padding_start)
        silence_end = AudioSegment.silent(duration=padding_end)
        
        # Add padding
        padded = silence_start + audio + silence_end
        padded.export(output_path, format='mp3')
        
        logger.info(f"Padding added: {input_path} (+{padding_start}ms, +{padding_end}ms)")
        return output_path
        
    except Exception as e:
        logger.error(f"Add padding failed: {e}")
        return input_path


# =========================================================================
# AUDIO QUALITY CHECKS
# =========================================================================

def validate_audio_quality(file_path: str) -> Dict:
    """
    Validate audio quality for learning platform.
    
    Args:
        file_path: Path to audio file
    
    Returns:
        Dict with validation results
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'metadata': {}
    }
    
    if not os.path.exists(file_path):
        result['valid'] = False
        result['errors'].append("File not found")
        return result
    
    # Get metadata
    metadata = get_audio_metadata(file_path)
    result['metadata'] = metadata
    
    # Check file size
    if metadata['file_size'] == 0:
        result['valid'] = False
        result['errors'].append("File is empty")
    elif metadata['file_size'] < 1024:  # Less than 1KB
        result['warnings'].append("File size very small, may be corrupt")
    
    # Check duration
    if metadata['duration'] == 0:
        result['valid'] = False
        result['errors'].append("Duration is 0 seconds")
    elif metadata['duration'] < 0.5:
        result['warnings'].append("Duration very short (< 0.5s)")
    elif metadata['duration'] > 300:  # 5 minutes
        result['warnings'].append("Duration very long (> 5 minutes)")
    
    # Check bitrate
    if metadata['bitrate'] > 0:
        if metadata['bitrate'] < 64000:  # 64 kbps
            result['warnings'].append("Low bitrate, may affect quality")
        elif metadata['bitrate'] > 320000:  # 320 kbps
            result['warnings'].append("Very high bitrate, consider compression")
    
    # Check sample rate
    if metadata['sample_rate'] > 0:
        if metadata['sample_rate'] < 22050:
            result['warnings'].append("Low sample rate")
    
    return result


# =========================================================================
# HELPER FUNCTIONS
# =========================================================================

def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted string (e.g., "1:23", "0:05")
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"


def get_audio_file_info_summary(file_path: str) -> str:
    """
    Get a human-readable summary of audio file info.
    
    Args:
        file_path: Path to audio file
    
    Returns:
        Summary string
    """
    if not os.path.exists(file_path):
        return "File not found"
    
    metadata = get_audio_metadata(file_path)
    
    duration_str = format_duration(metadata['duration'])
    size_kb = metadata['file_size'] / 1024
    bitrate_kbps = metadata['bitrate'] / 1000 if metadata['bitrate'] > 0 else 0
    
    return (
        f"{Path(file_path).name} | "
        f"Duration: {duration_str} | "
        f"Size: {size_kb:.1f} KB | "
        f"Bitrate: {bitrate_kbps:.0f} kbps | "
        f"Format: {metadata['format'].upper()}"
    )


def cleanup_temp_audio_files(directory: str, max_age_hours: int = 24):
    """
    Clean up temporary audio files older than specified hours.
    
    Args:
        directory: Directory to clean
        max_age_hours: Maximum age in hours
    """
    if not os.path.isdir(directory):
        logger.warning(f"Directory not found: {directory}")
        return
    
    from datetime import datetime, timedelta
    
    cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
    removed_count = 0
    
    for filename in os.listdir(directory):
        if not filename.startswith('tts_') and not filename.startswith('temp_'):
            continue
        
        file_path = os.path.join(directory, filename)
        
        if not os.path.isfile(file_path):
            continue
        
        # Check file age
        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        
        if file_time < cutoff_time:
            try:
                os.remove(file_path)
                removed_count += 1
            except Exception as e:
                logger.error(f"Failed to remove {filename}: {e}")
    
    if removed_count > 0:
        logger.info(f"Cleaned up {removed_count} temporary audio files from {directory}")

