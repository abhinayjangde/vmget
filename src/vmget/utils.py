"""Utility functions for vmget."""

import os
import shutil
import urllib.request
from urllib.error import URLError
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
        from vmget.colors import info, highlight

        print(f"{info('Created directory:')} {highlight(path)}")
        return True
    except OSError as e:
        from vmget.colors import print_error

        print_error(f"Error: Could not create directory '{path}': {e}")
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


def format_time(seconds: int | float | None) -> str:
    """Format seconds to human-readable time string.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted time string (e.g., "1:23:45" or "12:34")
    """
    if seconds is None or seconds < 0:
        return "--:--"

    seconds = int(seconds)

    if seconds >= 3600:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"


def read_urls_from_file(filepath: str) -> list[str]:
    """Read URLs from a text file (one URL per line).

    Args:
        filepath: Path to the file containing URLs

    Returns:
        List of URLs (empty lines and comments starting with # are ignored)
    """
    urls = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith("#"):
                    urls.append(line)
    except FileNotFoundError:
        from vmget.colors import print_error

        print_error(f"Error: File not found: {filepath}")
    except IOError as e:
        from vmget.colors import print_error

        print_error(f"Error reading file {filepath}: {e}")

    return urls


def expand_url(url: str) -> str:
    """Expand shortened URLs to their final destination.

    Args:
        url: Potentially shortened URL

    Returns:
        Expanded URL or original URL if expansion fails
    """
    known_shorteners = {
        "amzn.in",
        "amzn.com",
        "amzn.to",
        "bit.ly",
        "goo.gl",
        "tinyurl.com",
        "ow.ly",
        "t.co",
    }

    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.netloc.lower() in known_shorteners or any(
            parsed.netloc.lower().endswith("." + s) for s in known_shorteners
        ):
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
            )
            with urllib.request.urlopen(request, timeout=10) as response:
                expanded = response.url
                if expanded and expanded != url:
                    from vmget.colors import info, highlight

                    print(
                        f"{info('Expanded URL:')} {highlight(url)} -> {highlight(expanded)}"
                    )
                    return expanded
    except URLError:
        pass
    except Exception:
        pass

    return url
