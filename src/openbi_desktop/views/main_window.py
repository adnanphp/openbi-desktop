"""Main application window: sidebar + stacked views."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from openbi_desktop.config import AppConfig
from openbi_desktop.views.connect import ConnectView
from openbi_desktop.views.customers import CustomersView
from openbi_desktop.views.dashboard import DashboardView
from openbi_desktop.views.forecasts import ForecastsView


class MainWindow(QMainWindow):
    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self._config = config
        self.setWindowTitle("OpenBI Desktop")

        # Restore geometry from config.
        w = config.window
        self.resize(w.width, w.height)
        if w.x >= 0 and w.y >= 0:
            self.move(w.x, w.y)

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
        self._customers_view = CustomersView(self._config)
        self._forecasts_view = ForecastsView(self._config)

        self._add_view("Connect", self._connect_view)
        self._add_view("Dashboard", self._dashboard_view)
        self._add_view("Customers", self._customers_view)
        self._add_view("Forecasts", self._forecasts_view)

        self._sidebar.currentRowChanged.connect(self._stack.setCurrentIndex)
        self._sidebar.setCurrentRow(0)

        outer.addWidget(self._sidebar)
        outer.addWidget(self._stack, 1)

        self._connect_view.connected.connect(self._on_connected)

    def _add_view(self, label: str, widget: QWidget) -> None:
        item = QListWidgetItem(label)
        self._sidebar.addItem(item)
        self._stack.addWidget(widget)

    def _on_connected(self, url: str) -> None:
        self._config.api_url = url

    def closeEvent(self, event) -> None:  # noqa: N802 (Qt override)
        """Save window geometry on close."""
        geo = self.geometry()
        self._config.window.width = geo.width()
        self._config.window.height = geo.height()
        self._config.window.x = geo.x()
        self._config.window.y = geo.y()
        try:
            self._config.save()
        except OSError:
            pass  # don't block shutdown if save fails
        super().closeEvent(event)
