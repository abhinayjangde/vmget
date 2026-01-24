"""Configuration constants for vmget."""

# Default video quality when not specified
DEFAULT_VIDEO_QUALITY = "720p"

# Default audio quality (kbps) for MP3 conversion
DEFAULT_AUDIO_QUALITY = "192"

# Supported video qualities
SUPPORTED_QUALITIES = ["360p", "480p", "720p", "1080p", "1440p", "2160p", "best"]

# Supported output formats
# Video formats
VIDEO_FORMATS = ["mp4", "webm", "mkv"]
# Audio formats
AUDIO_FORMATS = ["mp3", "m4a", "wav", "flac", "aac", "opus"]
# All supported formats
SUPPORTED_FORMATS = VIDEO_FORMATS + AUDIO_FORMATS

# Format to codec mapping for audio extraction
AUDIO_CODEC_MAP = {
    "mp3": "mp3",
    "m4a": "m4a",
    "wav": "wav",
    "flac": "flac",
    "aac": "aac",
    "opus": "opus",
}

# Characters allowed in playlist folder names
SAFE_FILENAME_CHARS = " -_"

# Progress bar settings
PROGRESS_BAR_WIDTH = 40
