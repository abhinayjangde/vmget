"""User configuration file handling for vmget."""

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from vmget.config import (
    DEFAULT_VIDEO_QUALITY,
    SUPPORTED_FORMATS,
    SUPPORTED_QUALITIES,
)


@dataclass
class UserConfig:
    """User configuration settings."""

    # Default format for downloads
    format: str = "mp4"
    # Default quality for video downloads
    quality: str = DEFAULT_VIDEO_QUALITY
    # Default output directory (None means current directory)
    output_dir: str | None = None
    # Whether to show progress by default
    show_progress: bool = True
    # Whether to save thumbnails by default
    thumbnail: bool = False

    def validate(self) -> list[str]:
        """Validate configuration values.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if self.format and self.format.lower() not in SUPPORTED_FORMATS:
            errors.append(
                f"Invalid format '{self.format}'. "
                f"Supported: {', '.join(SUPPORTED_FORMATS)}"
            )

        if self.quality and self.quality.lower() not in SUPPORTED_QUALITIES:
            errors.append(
                f"Invalid quality '{self.quality}'. "
                f"Supported: {', '.join(SUPPORTED_QUALITIES)}"
            )

        if self.output_dir:
            expanded = os.path.expanduser(self.output_dir)
            if not os.path.isdir(expanded) and os.path.exists(expanded):
                errors.append(
                    f"Output path '{self.output_dir}' exists but is not a directory"
                )

        return errors


def get_config_paths() -> list[Path]:
    """Get list of possible configuration file paths in priority order.

    Returns:
        List of Path objects for possible config file locations
    """
    paths = []

    # Check for VMGET_CONFIG environment variable first
    env_config = os.environ.get("VMGET_CONFIG")
    if env_config:
        paths.append(Path(env_config))

    # Get home directory
    home = Path.home()

    # Platform-specific config locations
    if sys.platform == "win32":
        # Windows: Check APPDATA and home directory
        appdata = os.environ.get("APPDATA")
        if appdata:
            paths.append(Path(appdata) / "vmget" / "config.toml")
        paths.append(home / "vmget.toml")
        paths.append(home / ".vmgetrc")
    else:
        # Unix-like: Follow XDG spec and common conventions
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config:
            paths.append(Path(xdg_config) / "vmget" / "config.toml")
        else:
            paths.append(home / ".config" / "vmget" / "config.toml")
        paths.append(home / ".vmgetrc")
        paths.append(home / "vmget.toml")

    return paths


def _parse_toml_simple(content: str) -> dict[str, Any]:
    """Parse a simple TOML file without external dependencies.

    This is a basic parser that handles simple key-value pairs.
    For full TOML support, use tomllib (Python 3.11+).

    Args:
        content: TOML file content

    Returns:
        Dictionary of parsed values
    """
    result: dict[str, Any] = {}

    for line in content.splitlines():
        # Strip whitespace
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith("#"):
            continue

        # Skip section headers (we flatten everything for simplicity)
        if line.startswith("["):
            continue

        # Parse key = value
        if "=" in line:
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()

            # Parse value based on type
            if value.lower() in ("true", "false"):
                result[key] = value.lower() == "true"
            elif value.startswith('"') and value.endswith('"'):
                result[key] = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                result[key] = value[1:-1]
            else:
                # Try to parse as number
                try:
                    if "." in value:
                        result[key] = float(value)
                    else:
                        result[key] = int(value)
                except ValueError:
                    # Keep as string
                    result[key] = value

    return result


def _parse_toml(content: str) -> dict[str, Any]:
    """Parse TOML content using tomllib if available, fallback to simple parser.

    Args:
        content: TOML file content

    Returns:
        Dictionary of parsed values
    """
    try:
        import tomllib

        return tomllib.loads(content)
    except ImportError:
        return _parse_toml_simple(content)


def load_config() -> UserConfig:
    """Load user configuration from config file.

    Searches for config files in standard locations and returns
    a UserConfig with values from the first found config file.

    Returns:
        UserConfig instance (with defaults if no config file found)
    """
    config = UserConfig()

    for config_path in get_config_paths():
        if config_path.exists():
            try:
                content = config_path.read_text(encoding="utf-8")
                data = _parse_toml(content)

                # Map config file keys to UserConfig fields
                if "format" in data:
                    config.format = str(data["format"]).lower()
                if "quality" in data:
                    config.quality = str(data["quality"]).lower()
                if "output_dir" in data or "output" in data:
                    raw_dir = data.get("output_dir") or data.get("output")
                    config.output_dir = os.path.expanduser(str(raw_dir))
                if "show_progress" in data:
                    config.show_progress = bool(data["show_progress"])
                if "progress" in data:
                    config.show_progress = bool(data["progress"])
                if "thumbnail" in data:
                    config.thumbnail = bool(data["thumbnail"])

                # Validate the config
                errors = config.validate()
                if errors:
                    from vmget.colors import print_warning

                    print_warning(f"Warning: Config file {config_path} has issues:")
                    for err in errors:
                        print_warning(f"  - {err}")

                return config

            except Exception as e:
                from vmget.colors import print_warning

                print_warning(f"Warning: Could not load config from {config_path}: {e}")

    return config


def get_sample_config() -> str:
    """Get sample configuration file content.

    Returns:
        Sample TOML configuration content
    """
    return """# VMGET Configuration File
# Place this file at one of these locations:
#   - ~/.vmgetrc
#   - ~/.config/vmget/config.toml (Linux/macOS)
#   - %APPDATA%\\vmget\\config.toml (Windows)
# Or set VMGET_CONFIG environment variable to a custom path.

# Default output format (mp4, webm, mkv, mp3, m4a, wav, flac, aac, opus)
format = "mp4"

# Default video quality (360p, 480p, 720p, 1080p, 1440p, 2160p, best)
quality = "720p"

# Default output directory (use ~ for home directory)
# output_dir = "~/Videos/vmget"

# Show progress bar during download
show_progress = true

# Save video thumbnail as JPG file
thumbnail = false
"""
