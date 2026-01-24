"""Tests for vmget CLI module."""

import pytest
from unittest.mock import patch, MagicMock

from vmget.cli import create_parser, main


class TestCreateParser:
    """Tests for create_parser function."""

    def test_parser_has_required_arguments(self):
        parser = create_parser()

        # Parse with minimum required arguments
        args = parser.parse_args(["https://youtube.com/watch?v=test", "mp4"])

        assert args.url == "https://youtube.com/watch?v=test"
        assert args.file_format == "mp4"

    def test_parser_accepts_quality(self):
        parser = create_parser()
        args = parser.parse_args(["https://youtube.com/watch?v=test", "mp4", "1080p"])

        assert args.quality == "1080p"

    def test_parser_accepts_output_directory(self):
        parser = create_parser()
        args = parser.parse_args(
            ["https://youtube.com/watch?v=test", "mp4", "-o", "/custom/path"]
        )

        assert args.output == "/custom/path"

    def test_parser_accepts_items_flag(self):
        parser = create_parser()
        args = parser.parse_args(
            ["https://youtube.com/playlist?list=test", "mp4", "--items", "1-5,10"]
        )

        assert args.items == "1-5,10"

    def test_parser_accepts_no_playlist_flag(self):
        parser = create_parser()
        args = parser.parse_args(
            ["https://youtube.com/watch?v=test&list=playlist", "mp4", "--no-playlist"]
        )

        assert args.no_playlist is True

    def test_parser_rejects_invalid_format(self):
        parser = create_parser()

        with pytest.raises(SystemExit):
            parser.parse_args(["https://youtube.com/watch?v=test", "avi"])

    def test_parser_accepts_best_quality(self):
        parser = create_parser()
        args = parser.parse_args(["https://youtube.com/watch?v=test", "mp4", "best"])

        assert args.quality == "best"

    def test_parser_accepts_high_quality_options(self):
        parser = create_parser()

        # Test 1440p
        args = parser.parse_args(["https://youtube.com/watch?v=test", "mp4", "1440p"])
        assert args.quality == "1440p"

        # Test 2160p (4K)
        args = parser.parse_args(["https://youtube.com/watch?v=test", "mp4", "2160p"])
        assert args.quality == "2160p"


class TestMain:
    """Tests for main function."""

    @patch("vmget.cli.download_content")
    @patch("vmget.cli.check_ffmpeg")
    def test_main_returns_zero_on_success(self, mock_ffmpeg, mock_download):
        mock_ffmpeg.return_value = True
        mock_download.return_value = True

        with patch("sys.argv", ["vmget", "https://youtube.com/watch?v=test", "mp4"]):
            result = main()

        assert result == 0

    @patch("vmget.cli.download_content")
    @patch("vmget.cli.check_ffmpeg")
    def test_main_returns_one_on_failure(self, mock_ffmpeg, mock_download):
        mock_ffmpeg.return_value = True
        mock_download.return_value = False

        with patch("sys.argv", ["vmget", "https://youtube.com/watch?v=test", "mp4"]):
            result = main()

        assert result == 1

    @patch("vmget.cli.download_content")
    @patch("vmget.cli.check_ffmpeg")
    def test_main_warns_about_missing_ffmpeg(self, mock_ffmpeg, mock_download, capsys):
        mock_ffmpeg.return_value = False
        mock_download.return_value = True

        with patch("sys.argv", ["vmget", "https://youtube.com/watch?v=test", "mp3"]):
            main()

        captured = capsys.readouterr()
        assert "FFmpeg not found" in captured.out

    @patch("vmget.cli.download_content")
    @patch("vmget.cli.check_ffmpeg")
    def test_main_passes_all_arguments(self, mock_ffmpeg, mock_download):
        mock_ffmpeg.return_value = True
        mock_download.return_value = True

        with patch(
            "sys.argv",
            [
                "vmget",
                "https://youtube.com/playlist?list=test",
                "mp4",
                "1080p",
                "-o",
                "/downloads",
                "--items",
                "1-5",
                "--no-playlist",
            ],
        ):
            main()

        mock_download.assert_called_once_with(
            url="https://youtube.com/playlist?list=test",
            quality="1080p",
            file_format="mp4",
            output_dir="/downloads",
            playlist_items="1-5",
            no_playlist=True,
        )
