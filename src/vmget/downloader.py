"""Core download functionality for vmget."""

import os
import sys
from yt_dlp import YoutubeDL
import yt_dlp

from vmget.config import (
    DEFAULT_VIDEO_QUALITY,
    DEFAULT_AUDIO_QUALITY,
    SUPPORTED_FORMATS,
    VIDEO_FORMATS,
    AUDIO_FORMATS,
    AUDIO_CODEC_MAP,
    PROGRESS_BAR_WIDTH,
)
from vmget.utils import sanitize_filename, ensure_directory, format_size, format_time
from vmget.colors import (
    success,
    error,
    warning,
    info,
    highlight,
    bold,
    dim,
    print_success,
    print_error,
    print_warning,
    print_info,
    Colors,
)


class ProgressHook:
    """Progress hook for displaying download progress."""

    def __init__(self, output_dir: str | None = None):
        self.current_file = None
        self.last_percent = -1
        self.output_dir = output_dir
        self.downloaded_files: list[str] = []

    def __call__(self, d: dict) -> None:
        """Handle progress updates from yt-dlp.

        Args:
            d: Progress dictionary from yt-dlp
        """
        if d["status"] == "downloading":
            self._show_progress(d)
        elif d["status"] == "finished":
            self._show_finished(d)
        elif d["status"] == "error":
            print(f"\n{error('Download error occurred.')}")

    def _show_progress(self, d: dict) -> None:
        """Display download progress bar."""
        filename = d.get("filename", "Unknown")

        # Get progress info
        total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
        downloaded = d.get("downloaded_bytes", 0)
        speed = d.get("speed", 0)
        eta = d.get("eta", 0)

        # Calculate percentage
        if total > 0:
            percent = (downloaded / total) * 100
        else:
            percent = 0

        # Only update on significant change (avoid flickering)
        if int(percent) == self.last_percent and self.current_file == filename:
            return

        self.last_percent = int(percent)
        self.current_file = filename

        # Build progress bar with color
        filled = int(PROGRESS_BAR_WIDTH * percent / 100)
        if Colors._enabled:
            bar = f"{Colors.GREEN}{'█' * filled}{Colors.RESET}{'░' * (PROGRESS_BAR_WIDTH - filled)}"
        else:
            bar = "█" * filled + "░" * (PROGRESS_BAR_WIDTH - filled)

        # Format speed and ETA
        speed_str = f"{format_size(speed)}/s" if speed else "---"
        eta_str = format_time(eta) if eta else "--:--"
        size_str = (
            f"{format_size(downloaded)}/{format_size(total)}"
            if total
            else format_size(downloaded)
        )

        # Print progress line (overwrite previous)
        progress_line = (
            f"\r  [{bar}] {percent:5.1f}% | {size_str} | {speed_str} | ETA: {eta_str}"
        )
        sys.stdout.write(progress_line)
        sys.stdout.flush()

    def _show_finished(self, d: dict) -> None:
        """Display download finished message."""
        # Clear the progress line and show completion
        sys.stdout.write("\r" + " " * 100 + "\r")  # Clear line
        filepath = d.get("filename", "Unknown")
        filename = os.path.basename(filepath)
        total = d.get("total_bytes", 0)

        # Track downloaded files for final summary
        self.downloaded_files.append(filepath)

        if total:
            print(
                f"  {success('✓')} Downloaded: {highlight(filename)} ({format_size(total)})"
            )
        else:
            print(f"  {success('✓')} Downloaded: {highlight(filename)}")


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


def display_video_info(info_dict: dict) -> None:
    """Display video information before downloading.

    Args:
        info_dict: Video info dictionary from yt-dlp
    """
    title = info_dict.get("title", "Unknown")
    duration = info_dict.get("duration")
    uploader = info_dict.get("uploader", info_dict.get("channel"))
    view_count = info_dict.get("view_count")
    filesize = info_dict.get("filesize") or info_dict.get("filesize_approx")

    print()
    print(f"  {bold('Title:')}    {highlight(title)}")

    if uploader:
        print(f"  {bold('Channel:')}  {uploader}")

    if duration:
        print(f"  {bold('Duration:')} {format_time(duration)}")

    if filesize:
        print(f"  {bold('Size:')}     ~{format_size(filesize)}")

    if view_count:
        view_str = f"{view_count:,}" if isinstance(view_count, int) else str(view_count)
        print(f"  {bold('Views:')}    {view_str}")

    print()


def is_audio_format(file_format: str) -> bool:
    """Check if the format is an audio-only format.

    Args:
        file_format: Format string

    Returns:
        True if audio format, False otherwise
    """
    return file_format in AUDIO_FORMATS


def build_ydl_options(
    file_format: str,
    quality: str,
    output_dir: str,
    is_playlist: bool = False,
    show_progress: bool = True,
    write_thumbnail: bool = False,
    progress_hook: ProgressHook | None = None,
) -> dict:
    """Build yt-dlp options dictionary.

    Args:
        file_format: Output format (mp4, mp3, etc.)
        quality: Video quality (e.g., "720p", "best")
        output_dir: Output directory path
        is_playlist: Whether downloading a playlist
        show_progress: Whether to show progress bar
        write_thumbnail: Whether to save video thumbnail
        progress_hook: Optional ProgressHook instance to use

    Returns:
        yt-dlp options dictionary
    """
    # Base output template
    if is_playlist:
        outtmpl = os.path.join(output_dir, "%(playlist_index)s - %(title)s.%(ext)s")
    else:
        outtmpl = os.path.join(output_dir, "%(title)s.%(ext)s")

    # Base options
    ydl_opts = {
        "outtmpl": outtmpl,
        "quiet": True,
        "no_warnings": True,
    }

    # Add progress hook if enabled
    if show_progress:
        hook = progress_hook or ProgressHook(output_dir=output_dir)
        ydl_opts["progress_hooks"] = [hook]

    # Thumbnail options
    if write_thumbnail:
        ydl_opts["writethumbnail"] = True
        # Convert thumbnail to jpg for compatibility
        if "postprocessors" not in ydl_opts:
            ydl_opts["postprocessors"] = []
        ydl_opts["postprocessors"].append(
            {
                "key": "FFmpegThumbnailsConvertor",
                "format": "jpg",
            }
        )

    # Audio formats
    if is_audio_format(file_format):
        ydl_opts["format"] = "bestaudio/best"
        codec = AUDIO_CODEC_MAP.get(file_format, file_format)

        # Initialize postprocessors if not exists
        if "postprocessors" not in ydl_opts:
            ydl_opts["postprocessors"] = []

        # WAV doesn't need quality setting
        if file_format == "wav":
            ydl_opts["postprocessors"].append(
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": codec,
                }
            )
        else:
            ydl_opts["postprocessors"].append(
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": codec,
                    "preferredquality": DEFAULT_AUDIO_QUALITY,
                }
            )
    # Video formats
    else:
        # Handle "best" quality option
        if quality == "best":
            format_str = "bestvideo+bestaudio/best"
        else:
            height = quality[:-1]  # Remove 'p' from quality
            format_str = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"

        ydl_opts["format"] = format_str
        ydl_opts["merge_output_format"] = file_format

    return ydl_opts


def download_content(
    url: str,
    quality: str | None = None,
    file_format: str = "mp4",
    output_dir: str | None = None,
    playlist_items: str | None = None,
    no_playlist: bool = False,
    show_progress: bool = True,
    write_thumbnail: bool = False,
) -> bool:
    """Download video/audio or entire playlist.

    Args:
        url: Video or playlist URL
        quality: Video quality (360p, 480p, 720p, 1080p, 1440p, 2160p, best).
                 Defaults to 720p for video formats.
        file_format: Output format (mp4, webm, mp3, m4a, wav, flac, etc.)
        output_dir: Directory to save the file(s)
        playlist_items: Specific playlist items to download (e.g., "1-3,5,7-10")
        no_playlist: If True, download only the video, not the playlist
        show_progress: Whether to show progress bar
        write_thumbnail: Whether to save video thumbnail as JPG

    Returns:
        True if download succeeded, False otherwise
    """
    # Validate format
    if file_format not in SUPPORTED_FORMATS:
        print_error(
            f"Error: Unsupported format '{file_format}'. Use: {', '.join(SUPPORTED_FORMATS)}"
        )
        return False

    # Set default output directory
    if not output_dir:
        output_dir = os.getcwd()

    # Ensure output directory exists
    if not ensure_directory(output_dir):
        return False

    # Default quality for video formats if not specified
    if not is_audio_format(file_format) and not quality:
        quality = DEFAULT_VIDEO_QUALITY
        print(f"{info('No quality specified, defaulting to')} {highlight(quality)}")

    # Check if URL is a playlist
    playlist_info = None if no_playlist else get_playlist_info(url)

    if playlist_info:
        playlist_title = playlist_info.get("title", "Unknown Playlist")
        video_count = len(playlist_info.get("entries", []))
        print(f"{info('Detected playlist:')} {highlight(playlist_title)}")
        print(f"{info('Total videos in playlist:')} {highlight(str(video_count))}")

        # Create subfolder for playlist
        safe_title = sanitize_filename(playlist_title)
        output_dir = os.path.join(output_dir, safe_title)
        if not ensure_directory(output_dir):
            return False
    else:
        # Fetch and display video info for single videos
        video_info = get_video_info(url)
        if video_info:
            display_video_info(video_info)

    # Create progress hook to track downloaded files
    progress_hook = ProgressHook(output_dir=output_dir) if show_progress else None

    # Build yt-dlp options
    ydl_opts = build_ydl_options(
        file_format=file_format,
        quality=quality or DEFAULT_VIDEO_QUALITY,
        output_dir=output_dir,
        is_playlist=playlist_info is not None,
        show_progress=show_progress,
        write_thumbnail=write_thumbnail,
        progress_hook=progress_hook,
    )

    # Playlist-specific options
    if no_playlist:
        ydl_opts["noplaylist"] = True

    if playlist_items:
        ydl_opts["playlist_items"] = playlist_items
        print(f"{info('Downloading playlist items:')} {highlight(playlist_items)}")

    # Execute download
    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"{info('Downloading from:')} {dim(url)}")
            format_display = f"{highlight(file_format.upper())}" + (
                f" @ {highlight(quality)}"
                if quality and not is_audio_format(file_format)
                else ""
            )
            print(f"{info('Format:')} {format_display}")
            print()
            ydl.download([url])

            # Show completion message with file path
            print()
            print_success("Download completed successfully!")
            print(f"{info('Saved to:')} {highlight(os.path.abspath(output_dir))}")

            # List downloaded files if available
            if progress_hook and progress_hook.downloaded_files:
                if len(progress_hook.downloaded_files) == 1:
                    final_file = progress_hook.downloaded_files[0]
                    print(f"{info('File:')} {highlight(os.path.basename(final_file))}")

            return True
    except yt_dlp.utils.DownloadError as e:
        print_error(f"\nDownload error: {e}")
        return False
    except yt_dlp.utils.ExtractorError as e:
        print_error(f"\nExtractor error (invalid URL or unsupported site): {e}")
        return False
    except KeyboardInterrupt:
        print_warning("\n\nDownload cancelled by user.")
        return False
    except Exception as e:
        print_error(f"\nUnexpected error: {e}")
        return False


def download_multiple(
    urls: list[str],
    quality: str | None = None,
    file_format: str = "mp4",
    output_dir: str | None = None,
    playlist_items: str | None = None,
    no_playlist: bool = False,
    show_progress: bool = True,
    write_thumbnail: bool = False,
) -> tuple[int, int]:
    """Download multiple URLs.

    Args:
        urls: List of URLs to download
        quality: Video quality
        file_format: Output format
        output_dir: Directory to save files
        playlist_items: Specific playlist items
        no_playlist: If True, skip playlists
        show_progress: Whether to show progress bar
        write_thumbnail: Whether to save video thumbnail as JPG

    Returns:
        Tuple of (successful_count, failed_count)
    """
    total = len(urls)
    successful = 0
    failed = 0

    print(f"{info('Downloading')} {highlight(str(total))} {info('URL(s)...')}")
    print(bold("─" * 50))

    for i, url in enumerate(urls, 1):
        print(f"\n{info(f'[{i}/{total}]')} Processing URL...")

        result = download_content(
            url=url,
            quality=quality,
            file_format=file_format,
            output_dir=output_dir,
            playlist_items=playlist_items,
            no_playlist=no_playlist,
            show_progress=show_progress,
            write_thumbnail=write_thumbnail,
        )

        if result:
            successful += 1
        else:
            failed += 1

    print("\n" + bold("═" * 50))
    summary_parts = [
        success(f"{successful} successful"),
        error(f"{failed} failed") if failed > 0 else f"{failed} failed",
    ]
    print(f"{info('Completed:')} {', '.join(summary_parts)} out of {total} total")

    return successful, failed
