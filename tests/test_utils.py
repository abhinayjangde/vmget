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
    format_time,
    read_urls_from_file,
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


class TestFormatTime:
    """Tests for format_time function."""

    def test_seconds_only(self):
        assert format_time(45) == "00:45"

    def test_minutes_and_seconds(self):
        assert format_time(125) == "02:05"

    def test_hours_minutes_seconds(self):
        assert format_time(3661) == "1:01:01"

    def test_zero(self):
        assert format_time(0) == "00:00"

    def test_none(self):
        assert format_time(None) == "--:--"

    def test_negative(self):
        assert format_time(-10) == "--:--"

    def test_float_seconds(self):
        assert format_time(65.7) == "01:05"

    def test_large_value(self):
        assert format_time(7200) == "2:00:00"


class TestReadUrlsFromFile:
    """Tests for read_urls_from_file function."""

    def test_read_valid_file(self, tmp_path):
        # Create a test file with URLs
        url_file = tmp_path / "urls.txt"
        url_file.write_text(
            "https://youtube.com/watch?v=1\nhttps://youtube.com/watch?v=2\n"
        )

        urls = read_urls_from_file(str(url_file))
        assert len(urls) == 2
        assert urls[0] == "https://youtube.com/watch?v=1"
        assert urls[1] == "https://youtube.com/watch?v=2"

    def test_skip_empty_lines(self, tmp_path):
        url_file = tmp_path / "urls.txt"
        url_file.write_text("https://url1.com\n\n\nhttps://url2.com\n")

        urls = read_urls_from_file(str(url_file))
        assert len(urls) == 2

    def test_skip_comments(self, tmp_path):
        url_file = tmp_path / "urls.txt"
        url_file.write_text(
            "# This is a comment\nhttps://url1.com\n# Another comment\nhttps://url2.com\n"
        )

        urls = read_urls_from_file(str(url_file))
        assert len(urls) == 2
        assert urls[0] == "https://url1.com"

    def test_file_not_found(self, tmp_path, capsys):
        urls = read_urls_from_file(str(tmp_path / "nonexistent.txt"))
        assert urls == []
        captured = capsys.readouterr()
        assert "File not found" in captured.out

    def test_strips_whitespace(self, tmp_path):
        url_file = tmp_path / "urls.txt"
        url_file.write_text("  https://url1.com  \n  https://url2.com\t\n")

        urls = read_urls_from_file(str(url_file))
        assert urls[0] == "https://url1.com"
        assert urls[1] == "https://url2.com"
