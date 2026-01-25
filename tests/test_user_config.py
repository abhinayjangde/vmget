"""Tests for vmget user_config module."""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from vmget.user_config import (
    UserConfig,
    get_config_paths,
    load_config,
    get_sample_config,
    _parse_toml_simple,
)


class TestUserConfig:
    """Tests for UserConfig dataclass."""

    def test_default_values(self):
        config = UserConfig()
        assert config.format == "mp4"
        assert config.quality == "720p"
        assert config.output_dir is None
        assert config.show_progress is True
        assert config.thumbnail is False

    def test_validate_valid_config(self):
        config = UserConfig(format="mp4", quality="1080p")
        errors = config.validate()
        assert len(errors) == 0

    def test_validate_invalid_format(self):
        config = UserConfig(format="avi")
        errors = config.validate()
        assert len(errors) == 1
        assert "Invalid format" in errors[0]

    def test_validate_invalid_quality(self):
        config = UserConfig(quality="4k")
        errors = config.validate()
        assert len(errors) == 1
        assert "Invalid quality" in errors[0]


class TestGetConfigPaths:
    """Tests for get_config_paths function."""

    def test_returns_list_of_paths(self):
        paths = get_config_paths()
        assert isinstance(paths, list)
        assert all(isinstance(p, Path) for p in paths)

    @patch.dict(os.environ, {"VMGET_CONFIG": "/custom/config.toml"})
    def test_env_config_first(self):
        paths = get_config_paths()
        assert paths[0] == Path("/custom/config.toml")

    def test_includes_home_directory(self):
        paths = get_config_paths()
        path_strings = [str(p) for p in paths]
        home = str(Path.home())
        assert any(home in p for p in path_strings)


class TestParseTomlSimple:
    """Tests for _parse_toml_simple function."""

    def test_parse_string_value(self):
        content = 'format = "mp4"'
        result = _parse_toml_simple(content)
        assert result["format"] == "mp4"

    def test_parse_single_quoted_string(self):
        content = "format = 'webm'"
        result = _parse_toml_simple(content)
        assert result["format"] == "webm"

    def test_parse_boolean_true(self):
        content = "show_progress = true"
        result = _parse_toml_simple(content)
        assert result["show_progress"] is True

    def test_parse_boolean_false(self):
        content = "thumbnail = false"
        result = _parse_toml_simple(content)
        assert result["thumbnail"] is False

    def test_parse_integer(self):
        content = "max_downloads = 5"
        result = _parse_toml_simple(content)
        assert result["max_downloads"] == 5

    def test_skip_comments(self):
        content = "# This is a comment\nformat = 'mp4'"
        result = _parse_toml_simple(content)
        assert "This" not in result
        assert result["format"] == "mp4"

    def test_skip_empty_lines(self):
        content = "format = 'mp4'\n\n\nquality = '720p'"
        result = _parse_toml_simple(content)
        assert result["format"] == "mp4"
        assert result["quality"] == "720p"

    def test_skip_section_headers(self):
        content = "[section]\nformat = 'mp4'"
        result = _parse_toml_simple(content)
        assert result["format"] == "mp4"


class TestLoadConfig:
    """Tests for load_config function."""

    def test_returns_user_config(self):
        config = load_config()
        assert isinstance(config, UserConfig)

    def test_loads_from_file(self, tmp_path):
        config_file = tmp_path / ".vmgetrc"
        config_file.write_text('format = "webm"\nquality = "1080p"')

        with patch("vmget.user_config.get_config_paths", return_value=[config_file]):
            config = load_config()

        assert config.format == "webm"
        assert config.quality == "1080p"

    def test_expands_output_dir(self, tmp_path):
        config_file = tmp_path / ".vmgetrc"
        config_file.write_text('output_dir = "~/Videos"')

        with patch("vmget.user_config.get_config_paths", return_value=[config_file]):
            config = load_config()

        assert "~" not in config.output_dir
        assert "Videos" in config.output_dir

    def test_handles_missing_config(self, tmp_path):
        nonexistent = tmp_path / "nonexistent.toml"
        with patch("vmget.user_config.get_config_paths", return_value=[nonexistent]):
            config = load_config()

        # Should return defaults
        assert config.format == "mp4"


class TestGetSampleConfig:
    """Tests for get_sample_config function."""

    def test_returns_string(self):
        sample = get_sample_config()
        assert isinstance(sample, str)

    def test_contains_format_option(self):
        sample = get_sample_config()
        assert "format" in sample

    def test_contains_quality_option(self):
        sample = get_sample_config()
        assert "quality" in sample

    def test_contains_output_dir_option(self):
        sample = get_sample_config()
        assert "output_dir" in sample

    def test_is_valid_toml(self):
        sample = get_sample_config()
        # Should be parseable without errors
        result = _parse_toml_simple(sample)
        assert "format" in result
