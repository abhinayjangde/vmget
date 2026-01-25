"""Tests for vmget downloader module."""

import os
import pytest
from unittest.mock import patch, MagicMock

from vmget.downloader import (
    get_playlist_info,
    get_video_info,
    build_ydl_options,
    download_content,
    download_multiple,
    is_audio_format,
    ProgressHook,
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
    @patch("vmget.downloader.get_video_info")
    @patch("vmget.downloader.get_playlist_info")
    def test_successful_download(
        self, mock_playlist_info, mock_video_info, mock_ydl_class, tmp_path
    ):
        mock_playlist_info.return_value = None
        mock_video_info.return_value = {
            "title": "Test Video",
            "duration": 120,
            "uploader": "Test Channel",
        }

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
    @patch("vmget.downloader.get_video_info")
    @patch("vmget.downloader.get_playlist_info")
    def test_download_error_returns_false(
        self, mock_playlist_info, mock_video_info, mock_ydl_class, tmp_path
    ):
        import yt_dlp

        mock_playlist_info.return_value = None
        mock_video_info.return_value = {
            "title": "Test Video",
            "duration": 120,
            "uploader": "Test Channel",
        }

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
                with patch(
                    "vmget.downloader.get_video_info",
                    return_value={
                        "title": "Test Video",
                        "duration": 120,
                        "uploader": "Test Channel",
                    },
                ):
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
    @patch("vmget.downloader.get_video_info")
    @patch("vmget.downloader.get_playlist_info")
    def test_no_playlist_option(
        self, mock_playlist_info, mock_video_info, mock_ydl_class, tmp_path
    ):
        mock_playlist_info.return_value = None
        mock_video_info.return_value = {
            "title": "Test Video",
            "duration": 120,
            "uploader": "Test Channel",
        }

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


class TestIsAudioFormat:
    """Tests for is_audio_format function."""

    def test_mp3_is_audio(self):
        assert is_audio_format("mp3") is True

    def test_m4a_is_audio(self):
        assert is_audio_format("m4a") is True

    def test_wav_is_audio(self):
        assert is_audio_format("wav") is True

    def test_flac_is_audio(self):
        assert is_audio_format("flac") is True

    def test_aac_is_audio(self):
        assert is_audio_format("aac") is True

    def test_opus_is_audio(self):
        assert is_audio_format("opus") is True

    def test_mp4_is_not_audio(self):
        assert is_audio_format("mp4") is False

    def test_webm_is_not_audio(self):
        assert is_audio_format("webm") is False

    def test_mkv_is_not_audio(self):
        assert is_audio_format("mkv") is False


class TestBuildYdlOptionsFormats:
    """Tests for build_ydl_options with different formats."""

    def test_webm_format(self, tmp_path):
        opts = build_ydl_options("webm", "720p", str(tmp_path), is_playlist=False)
        assert opts["merge_output_format"] == "webm"

    def test_mkv_format(self, tmp_path):
        opts = build_ydl_options("mkv", "720p", str(tmp_path), is_playlist=False)
        assert opts["merge_output_format"] == "mkv"

    def test_m4a_format(self, tmp_path):
        opts = build_ydl_options("m4a", "720p", str(tmp_path), is_playlist=False)
        assert opts["format"] == "bestaudio/best"
        assert opts["postprocessors"][0]["preferredcodec"] == "m4a"

    def test_flac_format(self, tmp_path):
        opts = build_ydl_options("flac", "720p", str(tmp_path), is_playlist=False)
        assert opts["format"] == "bestaudio/best"
        assert opts["postprocessors"][0]["preferredcodec"] == "flac"

    def test_wav_format_no_quality(self, tmp_path):
        opts = build_ydl_options("wav", "720p", str(tmp_path), is_playlist=False)
        assert opts["postprocessors"][0]["preferredcodec"] == "wav"
        # WAV shouldn't have preferredquality
        assert "preferredquality" not in opts["postprocessors"][0]

    def test_progress_hook_disabled(self, tmp_path):
        opts = build_ydl_options("mp4", "720p", str(tmp_path), show_progress=False)
        assert "progress_hooks" not in opts

    def test_progress_hook_enabled(self, tmp_path):
        opts = build_ydl_options("mp4", "720p", str(tmp_path), show_progress=True)
        assert "progress_hooks" in opts
        assert len(opts["progress_hooks"]) == 1

    def test_thumbnail_disabled_by_default(self, tmp_path):
        opts = build_ydl_options("mp4", "720p", str(tmp_path))
        assert "writethumbnail" not in opts

    def test_thumbnail_enabled(self, tmp_path):
        opts = build_ydl_options("mp4", "720p", str(tmp_path), write_thumbnail=True)
        assert opts["writethumbnail"] is True
        assert "postprocessors" in opts
        # Find the thumbnail convertor postprocessor
        thumbnail_pp = None
        for pp in opts["postprocessors"]:
            if pp.get("key") == "FFmpegThumbnailsConvertor":
                thumbnail_pp = pp
                break
        assert thumbnail_pp is not None
        assert thumbnail_pp["format"] == "jpg"

    def test_thumbnail_with_audio_format(self, tmp_path):
        """Test that thumbnail works with audio formats (both postprocessors present)."""
        opts = build_ydl_options("mp3", "720p", str(tmp_path), write_thumbnail=True)
        assert opts["writethumbnail"] is True
        assert "postprocessors" in opts
        # Should have both FFmpegExtractAudio and FFmpegThumbnailsConvertor
        pp_keys = [pp.get("key") for pp in opts["postprocessors"]]
        assert "FFmpegThumbnailsConvertor" in pp_keys
        assert "FFmpegExtractAudio" in pp_keys


class TestProgressHook:
    """Tests for ProgressHook class."""

    def test_hook_creation(self):
        hook = ProgressHook()
        assert hook.current_file is None
        assert hook.last_percent == -1

    def test_hook_finished_status(self, capsys):
        hook = ProgressHook()
        hook(
            {
                "status": "finished",
                "filename": "/path/to/video.mp4",
                "total_bytes": 1024,
            }
        )
        captured = capsys.readouterr()
        assert "Downloaded" in captured.out


class TestDownloadMultiple:
    """Tests for download_multiple function."""

    @patch("vmget.downloader.download_content")
    def test_all_successful(self, mock_download, tmp_path):
        mock_download.return_value = True

        urls = ["https://url1.com", "https://url2.com", "https://url3.com"]
        successful, failed = download_multiple(
            urls=urls,
            file_format="mp4",
            output_dir=str(tmp_path),
        )

        assert successful == 3
        assert failed == 0
        assert mock_download.call_count == 3

    @patch("vmget.downloader.download_content")
    def test_some_failed(self, mock_download, tmp_path):
        mock_download.side_effect = [True, False, True]

        urls = ["https://url1.com", "https://url2.com", "https://url3.com"]
        successful, failed = download_multiple(
            urls=urls,
            file_format="mp4",
            output_dir=str(tmp_path),
        )

        assert successful == 2
        assert failed == 1

    @patch("vmget.downloader.download_content")
    def test_all_failed(self, mock_download, tmp_path):
        mock_download.return_value = False

        urls = ["https://url1.com", "https://url2.com"]
        successful, failed = download_multiple(
            urls=urls,
            file_format="mp4",
            output_dir=str(tmp_path),
        )

        assert successful == 0
        assert failed == 2

    @patch("vmget.downloader.download_content")
    def test_passes_options(self, mock_download, tmp_path):
        mock_download.return_value = True

        download_multiple(
            urls=["https://url1.com"],
            quality="1080p",
            file_format="webm",
            output_dir=str(tmp_path),
            playlist_items="1-5",
            no_playlist=True,
            show_progress=False,
            write_thumbnail=True,
        )

        mock_download.assert_called_once_with(
            url="https://url1.com",
            quality="1080p",
            file_format="webm",
            output_dir=str(tmp_path),
            playlist_items="1-5",
            no_playlist=True,
            show_progress=False,
            write_thumbnail=True,
        )
