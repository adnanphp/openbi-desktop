"""Application entry point."""

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from openbi_desktop.config import AppConfig
from openbi_desktop.views.main_window import MainWindow


def _icon_path() -> Path:
    return (
        Path(__file__).parent
        / "resources"
        / "icons"
        / "hicolor"
        / "scalable"
        / "apps"
        / "openbi-desktop.svg"
    )


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("OpenBI Desktop")
    app.setOrganizationName("OpenBI")
    app.setDesktopFileName("openbi-desktop")
    app.setWindowIcon(QIcon(str(_icon_path())))

    config = AppConfig.load()
    window = MainWindow(config)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
