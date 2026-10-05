"""Forecasts view — multi-model forecast chart + comparison table."""

from __future__ import annotations

from PySide6.QtCharts import (
    QBarCategoryAxis,
    QChart,
    QChartView,
    QLineSeries,
    QValueAxis,
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from openbi_desktop.api.client import OpenBIClient
from openbi_desktop.api.exceptions import OpenBIError
from openbi_desktop.api.models import ModelForecastSeries
from openbi_desktop.config import AppConfig


# Display color per model. Keys must match model_name from the API.
_MODEL_COLORS = {
    "ets": QColor("#2f80ed"),         # blue — the winner
    "xgboost": QColor("#b26a00"),     # amber
    "baseline_ma": QColor("#888888"), # grey
}


def _month_label(iso_date: str) -> str:
    """'2018-01-01' -> 'Jan 2018'."""
    try:
        year, month, _ = iso_date.split("-")
        names = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
        ]
        return f"{names[int(month) - 1]} {year}"
    except (ValueError, IndexError):
        return iso_date


class _ForecastsWorker(QThread):
    succeeded = Signal(object)  # list[ModelForecastSeries]
    failed = Signal(str)

    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url

    def run(self) -> None:
        try:
            client = OpenBIClient(self.base_url, timeout=15.0)
            series = client.forecast_series_by_model()
            self.succeeded.emit(series)
        except OpenBIError as exc:
            self.failed.emit(str(exc))
        except Exception as exc:
            self.failed.emit(f"Unexpected error: {exc}")


class ForecastsView(QWidget):
    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self._config = config
        self._worker: _ForecastsWorker | None = None

        self._build_ui()

    # -- UI ---------------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Sales Forecast")
        title.setStyleSheet("font-size: 22px; font-weight: 600;")
        header.addWidget(title)
        header.addStretch(1)

        self._refresh_button = QPushButton("Refresh")
        self._refresh_button.clicked.connect(self.refresh)
        header.addWidget(self._refresh_button)
        outer.addLayout(header)

        self._status = QLabel("")
        self._status.setStyleSheet("color: #666; font-size: 12px;")
        outer.addWidget(self._status)

        # Chart on top.
        self._chart = QChart()
        self._chart.legend().setVisible(True)
        self._chart.legend().setAlignment(Qt.AlignBottom)
        self._chart.setBackgroundBrush(QColor("#ffffff"))
        self._chart.setAnimationOptions(QChart.SeriesAnimations)

        self._chart_view = QChartView(self._chart)
        self._chart_view.setRenderHint(QPainter.Antialiasing)
        self._chart_view.setMinimumHeight(320)
        outer.addWidget(self._chart_view, 2)

        # Table below.
        table_label = QLabel("Model Comparison")
        table_label.setStyleSheet("font-size: 16px; font-weight: 600; margin-top: 8px;")
        outer.addWidget(table_label)

        self._table = QTableWidget()
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        outer.addWidget(self._table, 1)

    # -- data loading -----------------------------------------------------

    def refresh(self) -> None:
        self._refresh_button.setEnabled(False)
        self._status.setText("Loading …")
        self._status.setStyleSheet("color: #666; font-size: 12px;")

        self._worker = _ForecastsWorker(self._config.api_url)
        self._worker.succeeded.connect(self._on_success)
        self._worker.failed.connect(self._on_failure)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_success(self, series: list[ModelForecastSeries]) -> None:
        if not series:
            self._status.setText("No forecast data returned.")
            self._status.setStyleSheet("color: #b00020; font-size: 12px;")
            return

        months = [p.forecast_month for p in series[0].points]
        self._render_chart(series, months)
        self._render_table(series, months)

        winner = next((s for s in series if s.is_winner), series[0])
        self._status.setText(
            f"Loaded {len(series)} models • winner: {winner.display_name}"
        )
        self._status.setStyleSheet("color: #1a7f37; font-size: 12px;")

    def _on_failure(self, message: str) -> None:
        self._status.setText(f"Failed: {message}")
        self._status.setStyleSheet("color: #b00020; font-size: 12px;")

    def _on_finished(self) -> None:
        self._refresh_button.setEnabled(True)

    # -- chart ------------------------------------------------------------

    def _render_chart(
        self, series: list[ModelForecastSeries], months: list[str]
    ) -> None:
        self._chart.removeAllSeries()
        for axis in list(self._chart.axes()):
            self._chart.removeAxis(axis)

        # Category axis with month labels.
        axis_x = QBarCategoryAxis()
        axis_x.append([_month_label(m) for m in months])
        self._chart.addAxis(axis_x, Qt.AlignBottom)

        # Value axis from 0 to slightly above the max yhat.
        max_y = max(
            (p.yhat_upper or p.yhat) for s in series for p in s.points
        )
        axis_y = QValueAxis()
        axis_y.setRange(0, max_y * 1.15 if max_y > 0 else 1)
        axis_y.setLabelFormat("$%.0f")
        self._chart.addAxis(axis_y, Qt.AlignLeft)

        # One line series per model.
        for s in series:
            line = QLineSeries()
            line.setName(s.display_name)

            color = _MODEL_COLORS.get(s.model_name, QColor("#444444"))
            pen = QPen(color)
            pen.setWidth(3 if s.is_winner else 2)
            if not s.is_winner:
                pen.setStyle(Qt.DashLine)
            line.setPen(pen)

            for i, p in enumerate(s.points):
                line.append(i, p.yhat)

            self._chart.addSeries(line)
            line.attachAxis(axis_x)
            line.attachAxis(axis_y)

    # -- table ------------------------------------------------------------

    def _render_table(
        self, series: list[ModelForecastSeries], months: list[str]
    ) -> None:
        headers = ["Model"] + [_month_label(m) for m in months] + ["6-mo Total", ""]
        self._table.setColumnCount(len(headers))
        self._table.setHorizontalHeaderLabels(headers)
        self._table.setRowCount(len(series))

        bold = QFont()
        bold.setBold(True)

        for row, s in enumerate(series):
            name_item = QTableWidgetItem(s.display_name)
            if s.is_winner:
                name_item.setFont(bold)
                name_item.setForeground(QColor("#1a7f37"))
            self._table.setItem(row, 0, name_item)

            for col, p in enumerate(s.points, start=1):
                item = QTableWidgetItem(f"${p.yhat:,.0f}")
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self._table.setItem(row, col, item)

            total_item = QTableWidgetItem(f"${s.total:,.0f}")
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if s.is_winner:
                total_item.setFont(bold)
            self._table.setItem(row, len(months) + 1, total_item)

            winner_marker = QTableWidgetItem("🥇" if s.is_winner else "")
            winner_marker.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(row, len(months) + 2, winner_marker)

        hh = self._table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Stretch)
        for col in range(1, len(headers)):
            hh.setSectionResizeMode(col, QHeaderView.ResizeToContents)

    # -- lifecycle --------------------------------------------------------

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        if not self._status.text():
            self.refresh()
