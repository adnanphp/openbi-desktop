"""Connect view — configure and test the OpenBI backend URL."""

from __future__ import annotations

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from openbi_desktop.api.client import OpenBIClient
from openbi_desktop.api.exceptions import OpenBIError
from openbi_desktop.config import AppConfig


class _HealthCheckWorker(QThread):
    """Runs a /health check off the main thread."""

    succeeded = Signal(str)   # emits the status string
    failed = Signal(str)      # emits the error message

    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url

    def run(self) -> None:
        try:
            client = OpenBIClient(self.base_url, timeout=5.0)
            result = client.health()
            version = f" (v{result.version})" if result.version else ""
            self.succeeded.emit(f"Connected — status: {result.status}{version}")
        except OpenBIError as exc:
            self.failed.emit(str(exc))
        except Exception as exc:  # never let a thread die silently
            self.failed.emit(f"Unexpected error: {exc}")


class ConnectView(QWidget):
    """Screen for entering and testing the backend API URL."""

    connected = Signal(str)  # emitted with the validated URL

    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self._config = config
        self._worker: _HealthCheckWorker | None = None

        self._build_ui()
        self._load_config()

    # -- UI construction --------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title = QLabel("Connect to OpenBI")
        title.setStyleSheet("font-size: 22px; font-weight: 600;")
        layout.addWidget(title)

        subtitle = QLabel(
            "Enter the base URL of your OpenBI API service "
            "(for example, http://localhost:8000)."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #666;")
        layout.addWidget(subtitle)

        form = QFormLayout()
        self._url_input = QLineEdit()
        self._url_input.setPlaceholderText("http://localhost:8000")
        form.addRow("API URL:", self._url_input)
        layout.addLayout(form)

        button_row = QHBoxLayout()
        self._test_button = QPushButton("Test Connection")
        self._test_button.clicked.connect(self._on_test_clicked)
        self._save_button = QPushButton("Save")
        self._save_button.clicked.connect(self._on_save_clicked)
        button_row.addWidget(self._test_button)
        button_row.addWidget(self._save_button)
        button_row.addStretch(1)
        layout.addLayout(button_row)

        self._status_label = QLabel("")
        self._status_label.setWordWrap(True)
        self._status_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self._status_label)

        layout.addStretch(1)

    def _load_config(self) -> None:
        self._url_input.setText(self._config.api_url)

    # -- helpers ----------------------------------------------------------

    def _set_status(self, text: str, kind: str) -> None:
        """kind is 'info', 'success', or 'error'."""
        colors = {
            "info": "#444",
            "success": "#1a7f37",
            "error": "#b00020",
        }
        self._status_label.setStyleSheet(
            f"color: {colors.get(kind, '#444')}; font-size: 13px;"
        )
        self._status_label.setText(text)

    def _current_url(self) -> str:
        return self._url_input.text().strip()

    # -- slots ------------------------------------------------------------

    def _on_test_clicked(self) -> None:
        url = self._current_url()
        if not url:
            self._set_status("Please enter a URL first.", "error")
            return

        self._test_button.setEnabled(False)
        self._set_status(f"Testing {url} …", "info")

        self._worker = _HealthCheckWorker(url)
        self._worker.succeeded.connect(self._on_check_succeeded)
        self._worker.failed.connect(self._on_check_failed)
        self._worker.finished.connect(self._on_check_finished)
        self._worker.start()

    def _on_check_succeeded(self, message: str) -> None:
        self._set_status(message, "success")
        self.connected.emit(self._current_url())

    def _on_check_failed(self, message: str) -> None:
        self._set_status(f"Failed: {message}", "error")

    def _on_check_finished(self) -> None:
        self._test_button.setEnabled(True)

    def _on_save_clicked(self) -> None:
        url = self._current_url()
        if not url:
            self._set_status("Nothing to save — URL is empty.", "error")
            return
        self._config.api_url = url
        try:
            self._config.save()
        except OSError as exc:
            self._set_status(f"Could not save config: {exc}", "error")
            return
        self._set_status(f"Saved API URL: {url}", "success")
