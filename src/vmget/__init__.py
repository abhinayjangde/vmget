"""VMGET - Video/Audio Downloader CLI Tool.

A command-line tool for downloading videos and audio from YouTube
and 1000+ other sites using yt-dlp.
"""

__version__ = "0.2.0"
__author__ = "Abhi"
__description__ = "Fast and simple video/audio downloader for YouTube and 1000+ sites"

from vmget.downloader import download_content, get_playlist_info
from vmget.config import DEFAULT_VIDEO_QUALITY, DEFAULT_AUDIO_QUALITY

__all__ = [
    "__version__",
    "__author__",
    "__description__",
    "download_content",
    "get_playlist_info",
    "DEFAULT_VIDEO_QUALITY",
    "DEFAULT_AUDIO_QUALITY",
]
