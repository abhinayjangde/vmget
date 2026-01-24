"""Utility functions for vmget."""

import os
import shutil
from vmget.config import SAFE_FILENAME_CHARS


def sanitize_filename(filename: str) -> str:
    """Remove invalid characters from filename.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for filesystem
    """
    return "".join(
        c for c in filename if c.isalnum() or c in SAFE_FILENAME_CHARS
    ).strip()


def ensure_directory(path: str) -> bool:
    """Create directory if it doesn't exist.

    Args:
        path: Directory path to create

    Returns:
        True if directory exists or was created, False on error
    """
    if not path:
        return True

    if os.path.exists(path):
        return True

    try:
        os.makedirs(path)
        print(f"Created directory: {path}")
        return True
    except OSError as e:
        print(f"Error: Could not create directory '{path}': {e}")
        return False


def check_ffmpeg() -> bool:
    """Check if FFmpeg is installed and available in PATH.

    Returns:
        True if FFmpeg is available, False otherwise
    """
    return shutil.which("ffmpeg") is not None


def format_size(bytes_size: int) -> str:
    """Format bytes to human-readable size.

    Args:
        bytes_size: Size in bytes

    Returns:
        Human-readable size string (e.g., "1.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} PB"


def is_playlist_url(url: str) -> bool:
    """Check if URL likely contains a playlist.

    Args:
        url: URL to check

    Returns:
        True if URL appears to be a playlist
    """
    playlist_indicators = [
        "playlist?list=",
        "&list=",
        "/playlist/",
        "/sets/",  # SoundCloud
        "/album/",  # Bandcamp, Spotify
    ]
    return any(indicator in url.lower() for indicator in playlist_indicators)
