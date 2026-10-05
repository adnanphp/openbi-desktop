"""Application entry point."""

import sys

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("OpenBI Desktop")
        self.resize(900, 600)

        label = QLabel("OpenBI Desktop — skeleton running")
        label.setStyleSheet("font-size: 18px; padding: 24px;")
        self.setCentralWidget(label)


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("OpenBI Desktop")
    app.setOrganizationName("OpenBI")

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
