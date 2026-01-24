"""Configuration constants for vmget."""

# Default video quality when not specified
DEFAULT_VIDEO_QUALITY = "720p"

# Default audio quality (kbps) for MP3 conversion
DEFAULT_AUDIO_QUALITY = "192"

# Supported video qualities
SUPPORTED_QUALITIES = ["360p", "480p", "720p", "1080p", "1440p", "2160p", "best"]

# Supported output formats
SUPPORTED_FORMATS = ["mp4", "mp3"]

# Characters allowed in playlist folder names
SAFE_FILENAME_CHARS = " -_"
