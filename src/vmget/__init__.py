"""VMGET - Video/Audio Downloader CLI Tool.

A command-line tool for downloading videos and audio from YouTube
and 1000+ other sites using yt-dlp.
"""

__version__ = "1.0.4"
__author__ = "Abhi"
__description__ = "Fast and simple video/audio downloader for YouTube and 1000+ sites"

from vmget.downloader import download_content, download_multiple, get_playlist_info
from vmget.config import (
    DEFAULT_VIDEO_QUALITY,
    DEFAULT_AUDIO_QUALITY,
    SUPPORTED_FORMATS,
    VIDEO_FORMATS,
    AUDIO_FORMATS,
)
from vmget.user_config import load_config, get_sample_config, UserConfig

__all__ = [
    "__version__",
    "__author__",
    "__description__",
    "download_content",
    "download_multiple",
    "get_playlist_info",
    "DEFAULT_VIDEO_QUALITY",
    "DEFAULT_AUDIO_QUALITY",
    "SUPPORTED_FORMATS",
    "VIDEO_FORMATS",
    "AUDIO_FORMATS",
    "load_config",
    "get_sample_config",
    "UserConfig",
]
