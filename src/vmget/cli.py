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
from vmget.user_config import load_config, get_sample_config
from vmget.colors import (
    print_warning,
    print_error,
    print_info,
    print_success,
    highlight,
    bold,
    info,
)


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
            '  vmget "https://www.youtube.com/watch?v=VIDEO_ID" mp4 720p\n'
            '  vmget "https://www.youtube.com/watch?v=VIDEO_ID" mp4             # defaults to 720p\n'
            '  vmget "https://www.youtube.com/watch?v=VIDEO_ID" mp4 best        # best quality\n'
            '  vmget "https://www.youtube.com/watch?v=VIDEO_ID" mp3 -o ./downloads\n'
            "\n"
            "Using flags (alternative):\n"
            '  vmget "https://www.youtube.com/watch?v=VIDEO_ID" -F mp4 -q 720p\n'
            "\n"
            "Multiple URLs:\n"
            '  vmget "URL1" "URL2" "URL3" -F mp4 -q 720p                       # multiple URLs\n'
            "  vmget -f urls.txt -F mp4 -q 720p                                # from file\n"
            "\n"
            "Audio formats:\n"
            '  vmget "URL" mp3                                                 # MP3 audio\n'
            '  vmget "URL" flac                                                # FLAC lossless\n'
            '  vmget "URL" m4a                                                 # M4A audio\n'
            "\n"
            "Playlist examples:\n"
            '  vmget "https://www.youtube.com/playlist?list=ID" mp4 720p\n'
            '  vmget "https://www.youtube.com/playlist?list=ID" mp3 --items 1-5\n'
            '  vmget "URL" mp4 --no-playlist                                   # skip playlist\n'
            "\n"
            "Interactive mode:\n"
            "  vmget                                                           # prompts for URL and options\n"
            "  vmget -i                                                        # same as above\n"
            "\n"
            f"Video formats: {video_formats_str}\n"
            f"Audio formats: {audio_formats_str}\n"
            "\n"
            "Supported sites: YouTube, Vimeo, Twitter/X, TikTok, Instagram,\n"
            "                 SoundCloud, Bandcamp, Twitch, and 1000+ more!\n"
            "                 (Powered by yt-dlp - https://github.com/yt-dlp/yt-dlp)\n"
            "\n"
            "Configuration: Create ~/.vmgetrc or vmget.toml to set defaults.\n"
            "               Run 'vmget --show-config' to see sample config.\n"
            "\n"
            "Note: FFmpeg must be installed and in PATH for audio extraction."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "url",
        nargs="*",
        help="URL(s) of the video or playlist to download, optionally followed by format and quality",
    )
    parser.add_argument(
        "-F",
        "--format",
        dest="file_format",
        choices=SUPPORTED_FORMATS,
        default=None,
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
        default=None,
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
        "-i",
        "--interactive",
        action="store_true",
        help="Run in interactive mode (prompts for URL and options)",
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Show sample configuration file and exit",
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

    # Handle --show-config flag
    if args.show_config:
        print(get_sample_config())
        return 0

    # Load user configuration
    user_config = load_config()

    # Check if we should enter interactive mode
    # (no URLs provided and no file specified, or -i flag)
    if args.interactive or (not args.url and not args.file):
        from vmget.interactive import run_interactive_mode

        result = run_interactive_mode()
        if result is None:
            return 1

        # Use interactive mode results
        urls = [result["url"]]
        final_format = result["format"]
        final_quality = result["quality"]
        output_dir = result["output_dir"]
        write_thumbnail = result["thumbnail"]
        show_progress = True
        playlist_items = None
        no_playlist = False
    else:
        # Parse positional arguments intelligently
        urls = []
        positional_format = None
        positional_quality = None

        if args.url:
            # First positional argument is always treated as URL
            urls.append(args.url[0])

            # Check if we have more positional arguments
            if len(args.url) > 1:
                # Second argument: could be format or another URL
                second_arg = args.url[1].lower()
                if second_arg in SUPPORTED_FORMATS:
                    positional_format = second_arg

                    # Third argument: could be quality
                    if len(args.url) > 2:
                        third_arg = args.url[2].lower()
                        if third_arg in SUPPORTED_QUALITIES:
                            positional_quality = third_arg
                        else:
                            # It's another URL
                            urls.extend(args.url[2:])

                else:
                    # Second and subsequent arguments are URLs
                    urls.extend(args.url[1:])

        # Read URLs from file if specified
        if args.file:
            file_urls = read_urls_from_file(args.file)
            urls.extend(file_urls)

        # Check if we have any URLs
        if not urls:
            parser.print_help()
            print_error(
                "\nError: No URLs provided. Specify URLs or use -f/--file option."
            )
            print_info("Tip: Run 'vmget' without arguments for interactive mode.")
            return 1

        # Determine final format and quality (CLI args > positional args > config file)
        final_format = (
            args.file_format
            if args.file_format
            else (positional_format if positional_format else user_config.format)
        )
        final_quality = (
            args.quality
            if args.quality
            else (positional_quality if positional_quality else None)
        )

        # Determine output directory (CLI args > config file > current directory)
        output_dir = (
            args.output if args.output else (user_config.output_dir or os.getcwd())
        )

        # Show progress (CLI arg overrides config)
        show_progress = not args.no_progress and user_config.show_progress

        # Thumbnail (CLI arg OR config)
        write_thumbnail = args.thumbnail or user_config.thumbnail

        playlist_items = args.items
        no_playlist = args.no_playlist

    # Check if format requires FFmpeg
    if final_format in AUDIO_FORMATS and not check_ffmpeg():
        print_warning("Warning: FFmpeg not found in PATH. Audio extraction may fail.")
        print_info("Please install FFmpeg: https://ffmpeg.org/download.html")

    # Single URL or multiple URLs
    if len(urls) == 1:
        success = download_content(
            url=urls[0],
            quality=final_quality,
            file_format=final_format,
            output_dir=output_dir,
            playlist_items=playlist_items,
            no_playlist=no_playlist,
            show_progress=show_progress,
            write_thumbnail=write_thumbnail,
        )
        return 0 if success else 1
    else:
        successful, failed = download_multiple(
            urls=urls,
            quality=final_quality,
            file_format=final_format,
            output_dir=output_dir,
            playlist_items=playlist_items,
            no_playlist=no_playlist,
            show_progress=show_progress,
            write_thumbnail=write_thumbnail,
        )
        return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
