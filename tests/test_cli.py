"""Tests for vmget CLI module."""

import pytest
from unittest.mock import patch, MagicMock

from vmget.cli import create_parser, main


class TestCreateParser:
    """Tests for create_parser function."""

    def test_parser_has_required_arguments(self):
        parser = create_parser()

        # Parse with minimum required arguments (URL only, format defaults to mp4)
        args = parser.parse_args(["https://youtube.com/watch?v=test"])

        assert args.url == ["https://youtube.com/watch?v=test"]
        assert args.file_format == "mp4"  # default

    def test_parser_accepts_format_flag(self):
        parser = create_parser()
        args = parser.parse_args(["https://youtube.com/watch?v=test", "-F", "mp3"])

        assert args.file_format == "mp3"

    def test_parser_accepts_quality(self):
        parser = create_parser()
        args = parser.parse_args(["https://youtube.com/watch?v=test", "-q", "1080p"])

        assert args.quality == "1080p"

    def test_parser_accepts_output_directory(self):
        parser = create_parser()
        args = parser.parse_args(
            ["https://youtube.com/watch?v=test", "-o", "/custom/path"]
        )

        assert args.output == "/custom/path"

    def test_parser_accepts_items_flag(self):
        parser = create_parser()
        args = parser.parse_args(
            ["https://youtube.com/playlist?list=test", "--items", "1-5,10"]
        )

        assert args.items == "1-5,10"

    def test_parser_accepts_no_playlist_flag(self):
        parser = create_parser()
        args = parser.parse_args(
            ["https://youtube.com/watch?v=test&list=playlist", "--no-playlist"]
        )

        assert args.no_playlist is True

    def test_parser_rejects_invalid_format(self):
        parser = create_parser()

        with pytest.raises(SystemExit):
            parser.parse_args(["https://youtube.com/watch?v=test", "-F", "avi"])

    def test_parser_accepts_best_quality(self):
        parser = create_parser()
        args = parser.parse_args(["https://youtube.com/watch?v=test", "-q", "best"])

        assert args.quality == "best"

    def test_parser_accepts_high_quality_options(self):
        parser = create_parser()

        # Test 1440p
        args = parser.parse_args(["https://youtube.com/watch?v=test", "-q", "1440p"])
        assert args.quality == "1440p"

        # Test 2160p (4K)
        args = parser.parse_args(["https://youtube.com/watch?v=test", "-q", "2160p"])
        assert args.quality == "2160p"

    def test_parser_accepts_multiple_urls(self):
        parser = create_parser()
        args = parser.parse_args(
            ["https://url1.com", "https://url2.com", "https://url3.com", "-F", "mp4"]
        )

        assert len(args.url) == 3
        assert args.url[0] == "https://url1.com"
        assert args.url[2] == "https://url3.com"

    def test_parser_accepts_file_input(self):
        parser = create_parser()
        args = parser.parse_args(["-f", "urls.txt"])

        assert args.file == "urls.txt"

    def test_parser_accepts_no_progress_flag(self):
        parser = create_parser()
        args = parser.parse_args(["https://youtube.com/watch?v=test", "--no-progress"])

        assert args.no_progress is True

    def test_parser_accepts_thumbnail_flag(self):
        parser = create_parser()
        args = parser.parse_args(["https://youtube.com/watch?v=test", "--thumbnail"])

        assert args.thumbnail is True

    def test_parser_thumbnail_default_false(self):
        parser = create_parser()
        args = parser.parse_args(["https://youtube.com/watch?v=test"])

        assert args.thumbnail is False

    def test_parser_accepts_audio_formats(self):
        parser = create_parser()

        # Test various audio formats
        for fmt in ["mp3", "m4a", "wav", "flac", "aac", "opus"]:
            args = parser.parse_args(["https://youtube.com/watch?v=test", "-F", fmt])
            assert args.file_format == fmt

    def test_parser_accepts_video_formats(self):
        parser = create_parser()

        # Test various video formats
        for fmt in ["mp4", "webm", "mkv"]:
            args = parser.parse_args(["https://youtube.com/watch?v=test", "-F", fmt])
            assert args.file_format == fmt

    def test_parser_long_format_flag(self):
        parser = create_parser()
        args = parser.parse_args(
            ["https://youtube.com/watch?v=test", "--format", "webm"]
        )

        assert args.file_format == "webm"

    def test_parser_long_quality_flag(self):
        parser = create_parser()
        args = parser.parse_args(
            ["https://youtube.com/watch?v=test", "--quality", "720p"]
        )

        assert args.quality == "720p"


class TestMain:
    """Tests for main function."""

    @patch("vmget.cli.download_content")
    @patch("vmget.cli.check_ffmpeg")
    def test_main_returns_zero_on_success(self, mock_ffmpeg, mock_download):
        mock_ffmpeg.return_value = True
        mock_download.return_value = True

        with patch("sys.argv", ["vmget", "https://youtube.com/watch?v=test"]):
            result = main()

        assert result == 0

    @patch("vmget.cli.download_content")
    @patch("vmget.cli.check_ffmpeg")
    def test_main_returns_one_on_failure(self, mock_ffmpeg, mock_download):
        mock_ffmpeg.return_value = True
        mock_download.return_value = False

        with patch("sys.argv", ["vmget", "https://youtube.com/watch?v=test"]):
            result = main()

        assert result == 1

    @patch("vmget.cli.download_content")
    @patch("vmget.cli.check_ffmpeg")
    def test_main_warns_about_missing_ffmpeg(self, mock_ffmpeg, mock_download, capsys):
        mock_ffmpeg.return_value = False
        mock_download.return_value = True

        with patch(
            "sys.argv", ["vmget", "https://youtube.com/watch?v=test", "-F", "mp3"]
        ):
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
                "-F",
                "mp4",
                "-q",
                "1080p",
                "-o",
                "/downloads",
                "--items",
                "1-5",
                "--no-playlist",
                "--thumbnail",
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
            show_progress=True,
            write_thumbnail=True,
        )

    @patch("vmget.cli.download_multiple")
    @patch("vmget.cli.check_ffmpeg")
    def test_main_uses_download_multiple_for_multiple_urls(
        self, mock_ffmpeg, mock_download_multiple
    ):
        mock_ffmpeg.return_value = True
        mock_download_multiple.return_value = (2, 0)

        with patch(
            "sys.argv",
            [
                "vmget",
                "https://url1.com",
                "https://url2.com",
                "-F",
                "mp4",
            ],
        ):
            result = main()

        assert result == 0
        mock_download_multiple.assert_called_once()
        call_args = mock_download_multiple.call_args
        assert len(call_args.kwargs["urls"]) == 2

    @patch("vmget.cli.download_multiple")
    @patch("vmget.cli.read_urls_from_file")
    @patch("vmget.cli.check_ffmpeg")
    def test_main_reads_urls_from_file(
        self, mock_ffmpeg, mock_read_urls, mock_download_multiple
    ):
        mock_ffmpeg.return_value = True
        mock_read_urls.return_value = ["https://url1.com", "https://url2.com"]
        mock_download_multiple.return_value = (2, 0)

        with patch(
            "sys.argv",
            ["vmget", "-f", "urls.txt"],
        ):
            result = main()

        assert result == 0
        mock_read_urls.assert_called_once_with("urls.txt")
        mock_download_multiple.assert_called_once()

    def test_main_returns_error_when_no_urls(self, capsys):
        with patch("sys.argv", ["vmget"]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        assert "No URLs provided" in captured.out

    @patch("vmget.cli.download_content")
    @patch("vmget.cli.check_ffmpeg")
    def test_main_warns_for_all_audio_formats(self, mock_ffmpeg, mock_download, capsys):
        mock_ffmpeg.return_value = False
        mock_download.return_value = True

        for fmt in ["m4a", "wav", "flac", "aac", "opus"]:
            with patch(
                "sys.argv", ["vmget", "https://youtube.com/watch?v=test", "-F", fmt]
            ):
                main()

            captured = capsys.readouterr()
            assert "FFmpeg not found" in captured.out

    @patch("vmget.cli.download_content")
    @patch("vmget.cli.check_ffmpeg")
    def test_main_passes_no_progress_flag(self, mock_ffmpeg, mock_download):
        mock_ffmpeg.return_value = True
        mock_download.return_value = True

        with patch(
            "sys.argv",
            ["vmget", "https://youtube.com/watch?v=test", "--no-progress"],
        ):
            main()

        mock_download.assert_called_once()
        call_args = mock_download.call_args
        assert call_args.kwargs["show_progress"] is False

    @patch("vmget.cli.download_content")
    @patch("vmget.cli.check_ffmpeg")
    def test_main_default_format_is_mp4(self, mock_ffmpeg, mock_download):
        mock_ffmpeg.return_value = True
        mock_download.return_value = True

        with patch("sys.argv", ["vmget", "https://youtube.com/watch?v=test"]):
            main()

        mock_download.assert_called_once()
        call_args = mock_download.call_args
        assert call_args.kwargs["file_format"] == "mp4"

    @patch("vmget.cli.download_content")
    @patch("vmget.cli.check_ffmpeg")
    def test_main_passes_thumbnail_flag(self, mock_ffmpeg, mock_download):
        mock_ffmpeg.return_value = True
        mock_download.return_value = True

        with patch(
            "sys.argv",
            ["vmget", "https://youtube.com/watch?v=test", "--thumbnail"],
        ):
            main()

        mock_download.assert_called_once()
        call_args = mock_download.call_args
        assert call_args.kwargs["write_thumbnail"] is True

    @patch("vmget.cli.download_content")
    @patch("vmget.cli.check_ffmpeg")
    def test_main_thumbnail_default_false(self, mock_ffmpeg, mock_download):
        mock_ffmpeg.return_value = True
        mock_download.return_value = True

        with patch("sys.argv", ["vmget", "https://youtube.com/watch?v=test"]):
            main()

        mock_download.assert_called_once()
        call_args = mock_download.call_args
        assert call_args.kwargs["write_thumbnail"] is False
