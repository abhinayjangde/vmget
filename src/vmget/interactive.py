"""Interactive mode for vmget CLI."""

import sys
from vmget.config import (
    SUPPORTED_FORMATS,
    SUPPORTED_QUALITIES,
    VIDEO_FORMATS,
    AUDIO_FORMATS,
)
from vmget.colors import info, success, warning, error, highlight, bold


def prompt_input(message: str, default: str | None = None) -> str:
    """Prompt user for input with optional default.

    Args:
        message: Prompt message
        default: Default value if user presses Enter

    Returns:
        User input or default value
    """
    if default:
        prompt = f"{message} [{default}]: "
    else:
        prompt = f"{message}: "

    try:
        value = input(prompt).strip()
        return value if value else (default or "")
    except (EOFError, KeyboardInterrupt):
        print()
        raise KeyboardInterrupt


def prompt_choice(message: str, choices: list[str], default: str | None = None) -> str:
    """Prompt user to choose from a list of options.

    Args:
        message: Prompt message
        choices: List of valid choices
        default: Default choice if user presses Enter

    Returns:
        Selected choice
    """
    choices_display = ", ".join(choices)
    if default:
        prompt = f"{message} ({choices_display}) [{default}]: "
    else:
        prompt = f"{message} ({choices_display}): "

    while True:
        try:
            value = input(prompt).strip().lower()
            if not value and default:
                return default
            if value in [c.lower() for c in choices]:
                return value
            print(warning(f"Invalid choice. Please choose from: {choices_display}"))
        except (EOFError, KeyboardInterrupt):
            print()
            raise KeyboardInterrupt


def prompt_yes_no(message: str, default: bool = True) -> bool:
    """Prompt user for yes/no answer.

    Args:
        message: Prompt message
        default: Default value (True=yes, False=no)

    Returns:
        True for yes, False for no
    """
    if default:
        prompt = f"{message} [Y/n]: "
    else:
        prompt = f"{message} [y/N]: "

    try:
        value = input(prompt).strip().lower()
        if not value:
            return default
        return value in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        print()
        raise KeyboardInterrupt


def run_interactive_mode() -> dict | None:
    """Run interactive mode to gather download options.

    Returns:
        Dictionary with download options, or None if cancelled
    """
    print()
    print(bold(highlight("╔══════════════════════════════════════════════════╗")))
    print(bold(highlight("║          VMGET - Interactive Mode                ║")))
    print(bold(highlight("╚══════════════════════════════════════════════════╝")))
    print()

    try:
        # Get URL
        print(info("Enter the URL of the video or playlist to download."))
        print(info("Supports YouTube and 1000+ other sites."))
        print()
        url = prompt_input("URL")
        if not url:
            print(error("No URL provided. Exiting."))
            return None
        print()

        # Choose format category
        print(info("What would you like to download?"))
        print(f"  1. {highlight('video')} - Download as video file (mp4, webm, mkv)")
        print(f"  2. {highlight('audio')} - Download audio only (mp3, m4a, flac, etc.)")
        print()
        media_type = prompt_choice(
            "Download type", ["video", "audio", "1", "2"], "video"
        )
        if media_type in ("1", "video"):
            media_type = "video"
        else:
            media_type = "audio"
        print()

        # Choose specific format
        if media_type == "video":
            format_choices = VIDEO_FORMATS
            default_format = "mp4"
            print(info(f"Choose video format: {', '.join(format_choices)}"))
        else:
            format_choices = AUDIO_FORMATS
            default_format = "mp3"
            print(info(f"Choose audio format: {', '.join(format_choices)}"))

        file_format = prompt_choice("Format", format_choices, default_format)
        print()

        # Quality (only for video)
        quality = None
        if media_type == "video":
            print(info(f"Choose video quality: {', '.join(SUPPORTED_QUALITIES)}"))
            quality = prompt_choice("Quality", SUPPORTED_QUALITIES, "720p")
            print()

        # Output directory
        print(info("Enter output directory (leave empty for current directory)"))
        output_dir = prompt_input("Output directory", ".")
        print()

        # Thumbnail
        thumbnail = prompt_yes_no("Save video thumbnail?", False)
        print()

        # Summary
        print(bold("═" * 50))
        print(bold("Download Summary:"))
        print(f"  URL:       {highlight(url)}")
        print(f"  Format:    {highlight(file_format.upper())}")
        if quality:
            print(f"  Quality:   {highlight(quality)}")
        print(f"  Output:    {highlight(output_dir)}")
        print(f"  Thumbnail: {highlight('Yes' if thumbnail else 'No')}")
        print(bold("═" * 50))
        print()

        if not prompt_yes_no("Proceed with download?", True):
            print(warning("Download cancelled."))
            return None

        return {
            "url": url,
            "format": file_format,
            "quality": quality,
            "output_dir": output_dir,
            "thumbnail": thumbnail,
        }

    except KeyboardInterrupt:
        print()
        print(warning("\nInteractive mode cancelled."))
        return None
