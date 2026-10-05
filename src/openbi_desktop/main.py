"""Application entry point."""

import sys

from PySide6.QtWidgets import QApplication

from openbi_desktop.config import AppConfig
from openbi_desktop.views.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("OpenBI Desktop")
    app.setOrganizationName("OpenBI")

    config = AppConfig.load()
    window = MainWindow(config)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
