"""Core download functionality for vmget."""

import os
from yt_dlp import YoutubeDL
import yt_dlp

from vmget.config import DEFAULT_VIDEO_QUALITY, DEFAULT_AUDIO_QUALITY, SUPPORTED_FORMATS
from vmget.utils import sanitize_filename, ensure_directory


def get_playlist_info(url: str) -> dict | None:
    """Extract playlist information without downloading.

    Args:
        url: URL to check for playlist

    Returns:
        Playlist info dict if it's a playlist, None otherwise
    """
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "no_warnings": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info and info.get("_type") == "playlist":
                return info
            return None
    except Exception:
        return None


def get_video_info(url: str) -> dict | None:
    """Extract video information without downloading.

    Args:
        url: Video URL

    Returns:
        Video info dict or None on error
    """
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)
    except Exception:
        return None


def build_ydl_options(
    file_format: str,
    quality: str,
    output_dir: str,
    is_playlist: bool = False,
) -> dict:
    """Build yt-dlp options dictionary.

    Args:
        file_format: Output format (mp4 or mp3)
        quality: Video quality (e.g., "720p", "best")
        output_dir: Output directory path
        is_playlist: Whether downloading a playlist

    Returns:
        yt-dlp options dictionary
    """
    # Base output template
    if is_playlist:
        outtmpl = os.path.join(output_dir, "%(playlist_index)s - %(title)s.%(ext)s")
    else:
        outtmpl = os.path.join(output_dir, "%(title)s.%(ext)s")

    if file_format == "mp3":
        return {
            "format": "bestaudio/best",
            "outtmpl": outtmpl,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": DEFAULT_AUDIO_QUALITY,
                }
            ],
            "merge_output_format": "mp3",
        }
    else:
        # Handle "best" quality option
        if quality == "best":
            format_str = "bestvideo+bestaudio/best"
        else:
            height = quality[:-1]  # Remove 'p' from quality
            format_str = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"

        return {
            "format": format_str,
            "outtmpl": outtmpl,
            "merge_output_format": "mp4",
        }


def download_content(
    url: str,
    quality: str | None = None,
    file_format: str = "mp4",
    output_dir: str | None = None,
    playlist_items: str | None = None,
    no_playlist: bool = False,
) -> bool:
    """Download video/audio or entire playlist.

    Args:
        url: Video or playlist URL
        quality: Video quality (360p, 480p, 720p, 1080p, 1440p, 2160p, best).
                 Defaults to 720p for mp4.
        file_format: Output format (mp4 or mp3)
        output_dir: Directory to save the file(s)
        playlist_items: Specific playlist items to download (e.g., "1-3,5,7-10")
        no_playlist: If True, download only the video, not the playlist

    Returns:
        True if download succeeded, False otherwise
    """
    # Validate format
    if file_format not in SUPPORTED_FORMATS:
        print(
            f"Error: Unsupported format '{file_format}'. Use: {', '.join(SUPPORTED_FORMATS)}"
        )
        return False

    # Set default output directory
    if not output_dir:
        output_dir = os.getcwd()

    # Ensure output directory exists
    if not ensure_directory(output_dir):
        return False

    # Default quality for mp4 if not specified
    if file_format == "mp4" and not quality:
        quality = DEFAULT_VIDEO_QUALITY
        print(f"No quality specified, defaulting to {quality}")

    # Check if URL is a playlist
    playlist_info = None if no_playlist else get_playlist_info(url)

    if playlist_info:
        playlist_title = playlist_info.get("title", "Unknown Playlist")
        video_count = len(playlist_info.get("entries", []))
        print(f"Detected playlist: {playlist_title}")
        print(f"Total videos in playlist: {video_count}")

        # Create subfolder for playlist
        safe_title = sanitize_filename(playlist_title)
        output_dir = os.path.join(output_dir, safe_title)
        if not ensure_directory(output_dir):
            return False

    # Build yt-dlp options
    ydl_opts = build_ydl_options(
        file_format=file_format,
        quality=quality or DEFAULT_VIDEO_QUALITY,
        output_dir=output_dir,
        is_playlist=playlist_info is not None,
    )

    # Playlist-specific options
    if no_playlist:
        ydl_opts["noplaylist"] = True

    if playlist_items:
        ydl_opts["playlist_items"] = playlist_items
        print(f"Downloading playlist items: {playlist_items}")

    # Execute download
    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading from: {url}")
            ydl.download([url])
            print("Download completed successfully!")
            return True
    except yt_dlp.utils.DownloadError as e:
        print(f"Download error: {e}")
        return False
    except yt_dlp.utils.ExtractorError as e:
        print(f"Extractor error (invalid URL or unsupported site): {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
