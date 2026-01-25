"""Tests for vmget interactive module."""

import pytest
from unittest.mock import patch, MagicMock

from vmget.interactive import (
    prompt_input,
    prompt_choice,
    prompt_yes_no,
    run_interactive_mode,
)


class TestPromptInput:
    """Tests for prompt_input function."""

    def test_returns_user_input(self):
        with patch("builtins.input", return_value="test"):
            result = prompt_input("Enter value")
        assert result == "test"

    def test_returns_default_on_empty(self):
        with patch("builtins.input", return_value=""):
            result = prompt_input("Enter value", default="default")
        assert result == "default"

    def test_strips_whitespace(self):
        with patch("builtins.input", return_value="  test  "):
            result = prompt_input("Enter value")
        assert result == "test"

    def test_raises_keyboard_interrupt_on_eof(self):
        with patch("builtins.input", side_effect=EOFError):
            with pytest.raises(KeyboardInterrupt):
                prompt_input("Enter value")


class TestPromptChoice:
    """Tests for prompt_choice function."""

    def test_returns_valid_choice(self):
        with patch("builtins.input", return_value="mp4"):
            result = prompt_choice("Format", ["mp4", "webm", "mkv"])
        assert result == "mp4"

    def test_returns_default_on_empty(self):
        with patch("builtins.input", return_value=""):
            result = prompt_choice("Format", ["mp4", "webm"], default="mp4")
        assert result == "mp4"

    def test_case_insensitive(self):
        with patch("builtins.input", return_value="MP4"):
            result = prompt_choice("Format", ["mp4", "webm"])
        assert result == "mp4"


class TestPromptYesNo:
    """Tests for prompt_yes_no function."""

    def test_yes_returns_true(self):
        with patch("builtins.input", return_value="y"):
            result = prompt_yes_no("Continue?")
        assert result is True

    def test_no_returns_false(self):
        with patch("builtins.input", return_value="n"):
            result = prompt_yes_no("Continue?")
        assert result is False

    def test_empty_returns_default_true(self):
        with patch("builtins.input", return_value=""):
            result = prompt_yes_no("Continue?", default=True)
        assert result is True

    def test_empty_returns_default_false(self):
        with patch("builtins.input", return_value=""):
            result = prompt_yes_no("Continue?", default=False)
        assert result is False

    def test_yes_full_word(self):
        with patch("builtins.input", return_value="yes"):
            result = prompt_yes_no("Continue?")
        assert result is True


class TestRunInteractiveMode:
    """Tests for run_interactive_mode function."""

    def test_returns_dict_on_success(self):
        inputs = iter(
            [
                "https://youtube.com/watch?v=test",  # URL
                "video",  # Download type
                "mp4",  # Format
                "720p",  # Quality
                ".",  # Output directory
                "n",  # Thumbnail
                "y",  # Proceed
            ]
        )
        with patch("builtins.input", lambda _: next(inputs)):
            result = run_interactive_mode()

        assert result is not None
        assert result["url"] == "https://youtube.com/watch?v=test"
        assert result["format"] == "mp4"
        assert result["quality"] == "720p"

    def test_returns_none_on_cancel(self):
        with patch("builtins.input", side_effect=KeyboardInterrupt):
            result = run_interactive_mode()
        assert result is None

    def test_returns_none_on_empty_url(self):
        with patch("builtins.input", return_value=""):
            result = run_interactive_mode()
        assert result is None

    def test_audio_mode_no_quality(self):
        inputs = iter(
            [
                "https://youtube.com/watch?v=test",  # URL
                "audio",  # Download type
                "mp3",  # Format
                ".",  # Output directory
                "n",  # Thumbnail
                "y",  # Proceed
            ]
        )
        with patch("builtins.input", lambda _: next(inputs)):
            result = run_interactive_mode()

        assert result["format"] == "mp3"
        assert result["quality"] is None  # Audio doesn't have quality

    def test_returns_none_when_not_proceeding(self):
        inputs = iter(
            [
                "https://youtube.com/watch?v=test",  # URL
                "video",  # Download type
                "mp4",  # Format
                "720p",  # Quality
                ".",  # Output directory
                "n",  # Thumbnail
                "n",  # Don't proceed
            ]
        )
        with patch("builtins.input", lambda _: next(inputs)):
            result = run_interactive_mode()

        assert result is None
