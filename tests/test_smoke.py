"""Smoke test — package imports cleanly."""

import openbi_desktop


def test_version():
    assert openbi_desktop.__version__ == "0.1.0"
