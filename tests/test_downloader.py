"""Tests for vmget downloader module."""

import os
import pytest
from unittest.mock import patch, MagicMock

from vmget.downloader import (
    get_playlist_info,
    get_video_info,
    build_ydl_options,
    download_content,
)
from vmget.config import DEFAULT_VIDEO_QUALITY, DEFAULT_AUDIO_QUALITY


class TestBuildYdlOptions:
    """Tests for build_ydl_options function."""

    def test_mp3_options(self, tmp_path):
        opts = build_ydl_options("mp3", "720p", str(tmp_path), is_playlist=False)

        assert opts["format"] == "bestaudio/best"
        assert "postprocessors" in opts
        assert opts["postprocessors"][0]["key"] == "FFmpegExtractAudio"
        assert opts["postprocessors"][0]["preferredcodec"] == "mp3"
        assert opts["postprocessors"][0]["preferredquality"] == DEFAULT_AUDIO_QUALITY

    def test_mp4_options_720p(self, tmp_path):
        opts = build_ydl_options("mp4", "720p", str(tmp_path), is_playlist=False)

        assert "bestvideo[height<=720]" in opts["format"]
        assert opts["merge_output_format"] == "mp4"

    def test_mp4_options_1080p(self, tmp_path):
        opts = build_ydl_options("mp4", "1080p", str(tmp_path), is_playlist=False)

        assert "bestvideo[height<=1080]" in opts["format"]

    def test_mp4_options_best_quality(self, tmp_path):
        opts = build_ydl_options("mp4", "best", str(tmp_path), is_playlist=False)

        assert opts["format"] == "bestvideo+bestaudio/best"

    def test_playlist_output_template(self, tmp_path):
        opts = build_ydl_options("mp4", "720p", str(tmp_path), is_playlist=True)

        assert "%(playlist_index)s" in opts["outtmpl"]

    def test_single_video_output_template(self, tmp_path):
        opts = build_ydl_options("mp4", "720p", str(tmp_path), is_playlist=False)

        assert "%(playlist_index)s" not in opts["outtmpl"]
        assert "%(title)s" in opts["outtmpl"]


class TestGetPlaylistInfo:
    """Tests for get_playlist_info function."""

    @patch("vmget.downloader.YoutubeDL")
    def test_returns_playlist_info(self, mock_ydl_class):
        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info.return_value = {
            "_type": "playlist",
            "title": "Test Playlist",
            "entries": [{"id": "1"}, {"id": "2"}],
        }
        mock_ydl_class.return_value = mock_ydl

        result = get_playlist_info("https://youtube.com/playlist?list=test")

        assert result is not None
        assert result["title"] == "Test Playlist"
        assert len(result["entries"]) == 2

    @patch("vmget.downloader.YoutubeDL")
    def test_returns_none_for_single_video(self, mock_ydl_class):
        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info.return_value = {
            "_type": "video",
            "title": "Single Video",
        }
        mock_ydl_class.return_value = mock_ydl

        result = get_playlist_info("https://youtube.com/watch?v=test")

        assert result is None

    @patch("vmget.downloader.YoutubeDL")
    def test_returns_none_on_exception(self, mock_ydl_class):
        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info.side_effect = Exception("Network error")
        mock_ydl_class.return_value = mock_ydl

        result = get_playlist_info("https://invalid-url.com")

        assert result is None


class TestDownloadContent:
    """Tests for download_content function."""

    def test_invalid_format_returns_false(self, tmp_path):
        result = download_content(
            url="https://youtube.com/watch?v=test",
            file_format="avi",
            output_dir=str(tmp_path),
        )
        assert result is False

    @patch("vmget.downloader.YoutubeDL")
    @patch("vmget.downloader.get_playlist_info")
    def test_successful_download(self, mock_playlist_info, mock_ydl_class, tmp_path):
        mock_playlist_info.return_value = None

        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl.download.return_value = 0
        mock_ydl_class.return_value = mock_ydl

        result = download_content(
            url="https://youtube.com/watch?v=test",
            file_format="mp4",
            quality="720p",
            output_dir=str(tmp_path),
        )

        assert result is True

    @patch("vmget.downloader.YoutubeDL")
    @patch("vmget.downloader.get_playlist_info")
    def test_download_error_returns_false(
        self, mock_playlist_info, mock_ydl_class, tmp_path
    ):
        import yt_dlp

        mock_playlist_info.return_value = None

        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl.download.side_effect = yt_dlp.utils.DownloadError("Download failed")
        mock_ydl_class.return_value = mock_ydl

        result = download_content(
            url="https://youtube.com/watch?v=invalid",
            file_format="mp4",
            output_dir=str(tmp_path),
        )

        assert result is False

    def test_default_quality_for_mp4(self, tmp_path, capsys):
        with patch("vmget.downloader.YoutubeDL") as mock_ydl_class:
            with patch("vmget.downloader.get_playlist_info", return_value=None):
                mock_ydl = MagicMock()
                mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
                mock_ydl.__exit__ = MagicMock(return_value=False)
                mock_ydl_class.return_value = mock_ydl

                download_content(
                    url="https://youtube.com/watch?v=test",
                    file_format="mp4",
                    quality=None,  # No quality specified
                    output_dir=str(tmp_path),
                )

                captured = capsys.readouterr()
                assert "defaulting to 720p" in captured.out

    @patch("vmget.downloader.YoutubeDL")
    @patch("vmget.downloader.get_playlist_info")
    def test_no_playlist_option(self, mock_playlist_info, mock_ydl_class, tmp_path):
        mock_playlist_info.return_value = None

        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl_class.return_value = mock_ydl

        download_content(
            url="https://youtube.com/watch?v=test&list=playlist",
            file_format="mp4",
            output_dir=str(tmp_path),
            no_playlist=True,
        )

        # Verify noplaylist option was set
        call_args = mock_ydl_class.call_args
        assert call_args[0][0].get("noplaylist") is True
