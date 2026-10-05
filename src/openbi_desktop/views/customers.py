"""Customers view — RFM segment table."""

from __future__ import annotations

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QBrush, QColor, QFont
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
from openbi_desktop.api.models import CustomerSegment
from openbi_desktop.config import AppConfig


# Business-friendly colors for known segments.
_SEGMENT_COLORS = {
    "Champions": "#1a7f37",
    "Loyal Customers": "#2f80ed",
    "Potential Loyalists": "#2f80ed",
    "New Customers": "#2f80ed",
    "Need Attention": "#b26a00",
    "At Risk": "#b00020",
    "Lost": "#666666",
}


class _CustomersWorker(QThread):
    succeeded = Signal(object)  # list[CustomerSegment]
    failed = Signal(str)

    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url

    def run(self) -> None:
        try:
            client = OpenBIClient(self.base_url, timeout=15.0)
            segments = client.customer_segments()
            self.succeeded.emit(segments)
        except OpenBIError as exc:
            self.failed.emit(str(exc))
        except Exception as exc:
            self.failed.emit(f"Unexpected error: {exc}")


class CustomersView(QWidget):
    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self._config = config
        self._worker: _CustomersWorker | None = None

        self._build_ui()

    # -- UI ---------------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Customer Segments")
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

        self._table = QTableWidget()
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels(
            [
                "Segment",
                "Customers",
                "Recency (days)",
                "Frequency",
                "Avg Monetary",
                "Total Monetary",
            ]
        )
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.setSortingEnabled(False)

        hh = self._table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Stretch)
        for col in range(1, 6):
            hh.setSectionResizeMode(col, QHeaderView.ResizeToContents)

        outer.addWidget(self._table, 1)

        self._summary = QLabel("")
        self._summary.setStyleSheet("color: #444; font-size: 12px; padding-top: 4px;")
        outer.addWidget(self._summary)

    # -- data loading -----------------------------------------------------

    def refresh(self) -> None:
        self._refresh_button.setEnabled(False)
        self._status.setText("Loading …")
        self._status.setStyleSheet("color: #666; font-size: 12px;")

        self._worker = _CustomersWorker(self._config.api_url)
        self._worker.succeeded.connect(self._on_success)
        self._worker.failed.connect(self._on_failure)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_success(self, segments: list[CustomerSegment]) -> None:
        # Sort by total_monetary descending — biggest revenue segment first.
        segments = sorted(segments, key=lambda s: s.total_monetary, reverse=True)

        self._table.setRowCount(len(segments))
        bold = QFont()
        bold.setBold(True)

        for row, seg in enumerate(segments):
            name_item = QTableWidgetItem(seg.cluster_label)
            name_item.setFont(bold)
            color = _SEGMENT_COLORS.get(seg.cluster_label, "#1f2430")
            name_item.setForeground(QBrush(QColor(color)))
            self._table.setItem(row, 0, name_item)

            self._right_align_int(row, 1, seg.customers)
            self._right_align_float(row, 2, seg.avg_recency_days, decimals=1)
            self._right_align_float(row, 3, seg.avg_frequency, decimals=2)
            self._right_align_money(row, 4, seg.avg_monetary)
            self._right_align_money(row, 5, seg.total_monetary)

        total_customers = sum(s.customers for s in segments)
        total_revenue = sum(s.total_monetary for s in segments)

        self._status.setText(f"Loaded {len(segments)} segments")
        self._status.setStyleSheet("color: #1a7f37; font-size: 12px;")
        self._summary.setText(
            f"{total_customers:,} customers across all segments • "
            f"${total_revenue:,.0f} total historical revenue"
        )

    def _on_failure(self, message: str) -> None:
        self._status.setText(f"Failed: {message}")
        self._status.setStyleSheet("color: #b00020; font-size: 12px;")
        self._table.setRowCount(0)
        self._summary.setText("")

    def _on_finished(self) -> None:
        self._refresh_button.setEnabled(True)

    # -- table cell helpers ----------------------------------------------

    def _right_align_int(self, row: int, col: int, value: int) -> None:
        item = QTableWidgetItem(f"{value:,}")
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._table.setItem(row, col, item)

    def _right_align_float(self, row: int, col: int, value: float, decimals: int) -> None:
        item = QTableWidgetItem(f"{value:,.{decimals}f}")
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._table.setItem(row, col, item)

    def _right_align_money(self, row: int, col: int, value: float) -> None:
        item = QTableWidgetItem(f"${value:,.0f}")
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._table.setItem(row, col, item)

    # -- lifecycle --------------------------------------------------------

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        if not self._status.text():
            self.refresh()
