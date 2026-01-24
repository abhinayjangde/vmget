"""Command-line interface for vmget."""

import argparse
import os
import sys

from vmget import __version__, __description__
from vmget.config import (
    SUPPORTED_QUALITIES,
    SUPPORTED_FORMATS,
    VIDEO_FORMATS,
    AUDIO_FORMATS,
)
from vmget.downloader import download_content, download_multiple
from vmget.utils import check_ffmpeg, read_urls_from_file


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    # Format help strings
    video_formats_str = ", ".join(VIDEO_FORMATS)
    audio_formats_str = ", ".join(AUDIO_FORMATS)

    parser = argparse.ArgumentParser(
        prog="vmget",
        description=f"VMGET v{__version__} - {__description__}",
        epilog=(
            "Examples:\n"
            '  vmget "https://www.youtube.com/watch?v=VIDEO_ID" -F mp4 -q 720p\n'
            '  vmget "https://www.youtube.com/watch?v=VIDEO_ID" -F mp4          # defaults to 720p\n'
            '  vmget "https://www.youtube.com/watch?v=VIDEO_ID" -F mp4 -q best  # best quality\n'
            '  vmget "https://www.youtube.com/watch?v=VIDEO_ID" -F mp3 -o ./downloads\n'
            "\n"
            "Multiple URLs:\n"
            '  vmget "URL1" "URL2" "URL3" -F mp4 -q 720p                       # multiple URLs\n'
            "  vmget -f urls.txt -F mp4 -q 720p                                # from file\n"
            "\n"
            "Audio formats:\n"
            '  vmget "URL" -F mp3                                              # MP3 audio\n'
            '  vmget "URL" -F flac                                             # FLAC lossless\n'
            '  vmget "URL" -F m4a                                              # M4A audio\n'
            "\n"
            "Playlist examples:\n"
            '  vmget "https://www.youtube.com/playlist?list=ID" -F mp4 -q 720p\n'
            '  vmget "https://www.youtube.com/playlist?list=ID" -F mp3 --items 1-5\n'
            '  vmget "URL" -F mp4 --no-playlist                                # skip playlist\n'
            "\n"
            f"Video formats: {video_formats_str}\n"
            f"Audio formats: {audio_formats_str}\n"
            "\n"
            "Supported sites: YouTube and 1000+ other sites (powered by yt-dlp)\n"
            "Note: FFmpeg must be installed and in PATH for audio extraction."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "url",
        nargs="*",
        help="URL(s) of the video or playlist to download",
    )
    parser.add_argument(
        "-F",
        "--format",
        dest="file_format",
        choices=SUPPORTED_FORMATS,
        default="mp4",
        help=f"Output format (default: mp4). Options: {', '.join(SUPPORTED_FORMATS)}",
        metavar="FORMAT",
    )
    parser.add_argument(
        "-q",
        "--quality",
        choices=SUPPORTED_QUALITIES,
        default=None,
        help=f"Video quality (default: 720p). Options: {', '.join(SUPPORTED_QUALITIES)}",
        metavar="QUALITY",
    )
    parser.add_argument(
        "-f",
        "--file",
        help="Read URLs from a file (one URL per line)",
        metavar="FILE",
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
        "--no-progress",
        action="store_true",
        help="Disable progress bar display",
    )
    parser.add_argument(
        "--thumbnail",
        action="store_true",
        help="Save video thumbnail as JPG file",
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

    # Collect all URLs
    urls = list(args.url) if args.url else []

    # Read URLs from file if specified
    if args.file:
        file_urls = read_urls_from_file(args.file)
        urls.extend(file_urls)

    # Check if we have any URLs
    if not urls:
        parser.print_help()
        print("\nError: No URLs provided. Specify URLs or use -f/--file option.")
        return 1

    # Check if format requires FFmpeg
    if args.file_format in AUDIO_FORMATS and not check_ffmpeg():
        print("Warning: FFmpeg not found in PATH. Audio extraction may fail.")
        print("Please install FFmpeg: https://ffmpeg.org/download.html")

    show_progress = not args.no_progress

    # Single URL or multiple URLs
    if len(urls) == 1:
        success = download_content(
            url=urls[0],
            quality=args.quality,
            file_format=args.file_format,
            output_dir=args.output,
            playlist_items=args.items,
            no_playlist=args.no_playlist,
            show_progress=show_progress,
            write_thumbnail=args.thumbnail,
        )
        return 0 if success else 1
    else:
        successful, failed = download_multiple(
            urls=urls,
            quality=args.quality,
            file_format=args.file_format,
            output_dir=args.output,
            playlist_items=args.items,
            no_playlist=args.no_playlist,
            show_progress=show_progress,
            write_thumbnail=args.thumbnail,
        )
        return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
