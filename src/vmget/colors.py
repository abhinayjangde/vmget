"""Colored output utilities for vmget CLI."""

import sys
import os


def supports_color() -> bool:
    """Check if the terminal supports colored output.

    Returns:
        True if terminal supports colors, False otherwise
    """
    # Check if stdout is a TTY
    if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
        return False

    # Check for NO_COLOR environment variable (standard)
    if os.environ.get("NO_COLOR"):
        return False

    # Check for FORCE_COLOR environment variable
    if os.environ.get("FORCE_COLOR"):
        return True

    # Windows support
    if sys.platform == "win32":
        # Windows 10+ supports ANSI colors
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            # Enable ANSI escape codes on Windows
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            return True
        except Exception:
            # Check for Windows Terminal or VS Code
            if os.environ.get("WT_SESSION") or os.environ.get("TERM_PROGRAM"):
                return True
            return False

    # Unix-like systems
    return True


# ANSI color codes
class Colors:
    """ANSI color codes for terminal output."""

    # Check once at module load
    _enabled = supports_color()

    # Reset
    RESET = "\033[0m"

    # Colors
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright colors
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"

    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"

    @classmethod
    def disable(cls) -> None:
        """Disable colored output."""
        cls._enabled = False

    @classmethod
    def enable(cls) -> None:
        """Enable colored output (if terminal supports it)."""
        cls._enabled = supports_color()

    @classmethod
    def is_enabled(cls) -> bool:
        """Check if colors are enabled."""
        return cls._enabled


def _colorize(text: str, color: str) -> str:
    """Apply color to text if colors are enabled.

    Args:
        text: Text to colorize
        color: ANSI color code

    Returns:
        Colored text or original text if colors disabled
    """
    if Colors._enabled:
        return f"{color}{text}{Colors.RESET}"
    return text


def success(text: str) -> str:
    """Format text as success (green).

    Args:
        text: Text to format

    Returns:
        Green colored text
    """
    return _colorize(text, Colors.GREEN)


def error(text: str) -> str:
    """Format text as error (red).

    Args:
        text: Text to format

    Returns:
        Red colored text
    """
    return _colorize(text, Colors.RED)


def warning(text: str) -> str:
    """Format text as warning (yellow).

    Args:
        text: Text to format

    Returns:
        Yellow colored text
    """
    return _colorize(text, Colors.YELLOW)


def info(text: str) -> str:
    """Format text as info (blue).

    Args:
        text: Text to format

    Returns:
        Blue colored text
    """
    return _colorize(text, Colors.BLUE)


def highlight(text: str) -> str:
    """Format text as highlight (cyan).

    Args:
        text: Text to format

    Returns:
        Cyan colored text
    """
    return _colorize(text, Colors.CYAN)


def bold(text: str) -> str:
    """Format text as bold.

    Args:
        text: Text to format

    Returns:
        Bold text
    """
    return _colorize(text, Colors.BOLD)


def dim(text: str) -> str:
    """Format text as dim.

    Args:
        text: Text to format

    Returns:
        Dimmed text
    """
    return _colorize(text, Colors.DIM)


# Convenience print functions
def print_success(text: str) -> None:
    """Print success message (green)."""
    print(success(text))


def print_error(text: str) -> None:
    """Print error message (red) to stderr."""
    print(error(text), file=sys.stderr)


def print_warning(text: str) -> None:
    """Print warning message (yellow)."""
    print(warning(text))


def print_info(text: str) -> None:
    """Print info message (blue)."""
    print(info(text))


def print_highlight(text: str) -> None:
    """Print highlighted message (cyan)."""
    print(highlight(text))
