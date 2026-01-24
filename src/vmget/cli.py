"""Command-line interface for vmget."""

import argparse
import os
import sys

from vmget import __version__, __description__
from vmget.config import SUPPORTED_QUALITIES, SUPPORTED_FORMATS
from vmget.downloader import download_content
from vmget.utils import check_ffmpeg


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="vmget",
        description=f"VMGET v{__version__} - {__description__}",
        epilog=(
            "Examples:\n"
            '  vmget "https://www.youtube.com/watch?v=VIDEO_ID" mp4 720p\n'
            '  vmget "https://www.youtube.com/watch?v=VIDEO_ID" mp4          # defaults to 720p\n'
            '  vmget "https://www.youtube.com/watch?v=VIDEO_ID" mp4 best     # best available quality\n'
            '  vmget "https://www.youtube.com/watch?v=VIDEO_ID" mp3 -o C:\\Downloads\n'
            "\n"
            "Playlist examples:\n"
            '  vmget "https://www.youtube.com/playlist?list=PLAYLIST_ID" mp4 720p\n'
            '  vmget "https://www.youtube.com/playlist?list=PLAYLIST_ID" mp3 --items 1-5\n'
            '  vmget "https://www.youtube.com/watch?v=VIDEO_ID&list=PLAYLIST_ID" mp4 --no-playlist\n'
            "\n"
            "Supported sites: YouTube and 1000+ other sites (powered by yt-dlp)\n"
            "Note: FFmpeg must be installed and in PATH for audio extraction."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "url",
        help="URL of the video or playlist to download",
    )
    parser.add_argument(
        "file_format",
        choices=SUPPORTED_FORMATS,
        help=f"Desired file format ({', '.join(SUPPORTED_FORMATS)})",
    )
    parser.add_argument(
        "quality",
        nargs="?",
        choices=SUPPORTED_QUALITIES,
        help=f"Video quality ({', '.join(SUPPORTED_QUALITIES)}). Default: 720p",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output directory for the downloaded file(s)",
        default=os.getcwd(),
        metavar="DIR",
    )
    parser.add_argument(
        "--items",
        help="Playlist items to download (e.g., '1-3,5,7-10')",
        default=None,
        metavar="RANGE",
    )
    parser.add_argument(
        "--no-playlist",
        action="store_true",
        help="Download only the video, not the playlist (if URL contains both)",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return parser


def main() -> int:
    """Main entry point for vmget CLI.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = create_parser()
    args = parser.parse_args()

    # Warn if FFmpeg is not available (needed for audio extraction)
    if args.file_format == "mp3" and not check_ffmpeg():
        print("Warning: FFmpeg not found in PATH. Audio extraction may fail.")
        print("Please install FFmpeg: https://ffmpeg.org/download.html")

    success = download_content(
        url=args.url,
        quality=args.quality,
        file_format=args.file_format,
        output_dir=args.output,
        playlist_items=args.items,
        no_playlist=args.no_playlist,
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
