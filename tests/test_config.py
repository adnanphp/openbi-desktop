"""Tests for the config persistence layer."""

from pathlib import Path

from openbi_desktop.config import AppConfig


def test_defaults_when_file_missing(tmp_path: Path):
    cfg = AppConfig.load(tmp_path / "does-not-exist.toml")
    assert cfg.api_url == "http://localhost:8000"


def test_roundtrip(tmp_path: Path):
    path = tmp_path / "config.toml"
    original = AppConfig(api_url="http://example.test:9999")
    original.save(path)

    loaded = AppConfig.load(path)
    assert loaded.api_url == "http://example.test:9999"


def test_corrupt_file_falls_back_to_defaults(tmp_path: Path):
    path = tmp_path / "config.toml"
    path.write_text("this is not valid toml [[[")
    cfg = AppConfig.load(path)
    assert cfg.api_url == "http://localhost:8000"
