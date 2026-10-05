"""Main application window: sidebar + stacked views."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from openbi_desktop.config import AppConfig
from openbi_desktop.views.connect import ConnectView
from openbi_desktop.views.dashboard import DashboardView
from openbi_desktop.views.customers import CustomersView

class _PlaceholderView(QWidget):
    """Temporary placeholder until a real view is built."""

    def __init__(self, name: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        label = QLabel(f"{name}\n\n(coming soon)")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 16px; color: #888;")
        layout.addWidget(label)


class MainWindow(QMainWindow):
    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self._config = config
        self.setWindowTitle("OpenBI Desktop")
        self.resize(1100, 720)

        central = QWidget()
        self.setCentralWidget(central)

        outer = QHBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._sidebar = QListWidget()
        self._sidebar.setFixedWidth(200)
        self._sidebar.setStyleSheet(
            "QListWidget { background: #1f2430; color: #e6e6e6; border: none; }"
            "QListWidget::item { padding: 12px 16px; }"
            "QListWidget::item:selected { background: #2f80ed; color: white; }"
        )

        self._stack = QStackedWidget()

        self._connect_view = ConnectView(self._config)
        self._dashboard_view = DashboardView(self._config)

        self._add_view("Connect", self._connect_view)
        self._add_view("Dashboard", self._dashboard_view)
        self._customers_view = CustomersView(self._config)
        self._add_view("Customers", self._customers_view)
        self._add_view("Forecasts", _PlaceholderView("Forecasts"))

        self._sidebar.currentRowChanged.connect(self._stack.setCurrentIndex)
        self._sidebar.setCurrentRow(0)

        outer.addWidget(self._sidebar)
        outer.addWidget(self._stack, 1)

        # When the Connect view verifies a URL, propagate it to other views.
        self._connect_view.connected.connect(self._on_connected)

    def _add_view(self, label: str, widget: QWidget) -> None:
        item = QListWidgetItem(label)
        self._sidebar.addItem(item)
        self._stack.addWidget(widget)

    def _on_connected(self, url: str) -> None:
        self._config.api_url = url
