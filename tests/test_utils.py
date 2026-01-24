"""Tests for vmget utility functions."""

import os
import pytest
from unittest.mock import patch, MagicMock

from vmget.utils import (
    sanitize_filename,
    ensure_directory,
    check_ffmpeg,
    format_size,
    is_playlist_url,
)


class TestSanitizeFilename:
    """Tests for sanitize_filename function."""

    def test_removes_special_characters(self):
        assert sanitize_filename("Hello@World!") == "HelloWorld"

    def test_keeps_alphanumeric(self):
        assert sanitize_filename("Hello123World") == "Hello123World"

    def test_keeps_allowed_characters(self):
        assert sanitize_filename("Hello-World_Test") == "Hello-World_Test"

    def test_keeps_spaces(self):
        assert sanitize_filename("Hello World") == "Hello World"

    def test_strips_whitespace(self):
        assert sanitize_filename("  Hello World  ") == "Hello World"

    def test_empty_string(self):
        assert sanitize_filename("") == ""

    def test_only_special_characters(self):
        assert sanitize_filename("@#$%^&*()") == ""

    def test_unicode_characters(self):
        # Unicode alphanumeric characters are allowed by isalnum()
        result = sanitize_filename("Видео-Test")
        assert result == "Видео-Test"


class TestEnsureDirectory:
    """Tests for ensure_directory function."""

    def test_existing_directory(self, tmp_path):
        assert ensure_directory(str(tmp_path)) is True

    def test_create_new_directory(self, tmp_path):
        new_dir = tmp_path / "new_folder"
        assert ensure_directory(str(new_dir)) is True
        assert new_dir.exists()

    def test_create_nested_directory(self, tmp_path):
        nested_dir = tmp_path / "level1" / "level2" / "level3"
        assert ensure_directory(str(nested_dir)) is True
        assert nested_dir.exists()

    def test_empty_path(self):
        assert ensure_directory("") is True

    def test_none_path(self):
        assert ensure_directory(None) is True

    @patch("os.makedirs")
    def test_permission_error(self, mock_makedirs, tmp_path):
        mock_makedirs.side_effect = OSError("Permission denied")
        new_dir = tmp_path / "forbidden"
        # First check should pass (path doesn't exist), then makedirs fails
        with patch("os.path.exists", return_value=False):
            assert ensure_directory(str(new_dir)) is False


class TestCheckFfmpeg:
    """Tests for check_ffmpeg function."""

    @patch("shutil.which")
    def test_ffmpeg_available(self, mock_which):
        mock_which.return_value = "/usr/bin/ffmpeg"
        assert check_ffmpeg() is True
        mock_which.assert_called_once_with("ffmpeg")

    @patch("shutil.which")
    def test_ffmpeg_not_available(self, mock_which):
        mock_which.return_value = None
        assert check_ffmpeg() is False


class TestFormatSize:
    """Tests for format_size function."""

    def test_bytes(self):
        assert format_size(500) == "500.0 B"

    def test_kilobytes(self):
        assert format_size(1024) == "1.0 KB"

    def test_megabytes(self):
        assert format_size(1024 * 1024) == "1.0 MB"

    def test_gigabytes(self):
        assert format_size(1024 * 1024 * 1024) == "1.0 GB"

    def test_terabytes(self):
        assert format_size(1024**4) == "1.0 TB"

    def test_zero(self):
        assert format_size(0) == "0.0 B"

    def test_fractional_megabytes(self):
        assert format_size(int(1.5 * 1024 * 1024)) == "1.5 MB"


class TestIsPlaylistUrl:
    """Tests for is_playlist_url function."""

    def test_youtube_playlist_url(self):
        url = "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
        assert is_playlist_url(url) is True

    def test_youtube_video_with_playlist(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
        assert is_playlist_url(url) is True

    def test_youtube_single_video(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert is_playlist_url(url) is False

    def test_youtube_short_url(self):
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert is_playlist_url(url) is False

    def test_soundcloud_set(self):
        url = "https://soundcloud.com/artist/sets/album-name"
        assert is_playlist_url(url) is True

    def test_bandcamp_album(self):
        url = "https://artist.bandcamp.com/album/album-name"
        assert is_playlist_url(url) is True

    def test_empty_url(self):
        assert is_playlist_url("") is False
