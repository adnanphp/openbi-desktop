"""Dashboard view — KPI cards + monthly revenue chart."""

from __future__ import annotations

from PySide6.QtCharts import (
    QChart,
    QChartView,
    QLineSeries,
    QValueAxis,
    QCategoryAxis,
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from openbi_desktop.api.client import OpenBIClient
from openbi_desktop.api.exceptions import OpenBIError
from openbi_desktop.api.models import ExecutiveKPIs, MonthlyRevenuePoint
from openbi_desktop.config import AppConfig
from openbi_desktop.widgets.kpi_card import KPICard


class _DashboardWorker(QThread):
    """Fetches KPIs and monthly revenue off the main thread."""

    succeeded = Signal(object, object)  # ExecutiveKPIs, list[MonthlyRevenuePoint]
    failed = Signal(str)

    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url

    def run(self) -> None:
        try:
            client = OpenBIClient(self.base_url, timeout=15.0)
            kpis = client.executive_kpis()
            monthly = client.monthly_revenue()
            self.succeeded.emit(kpis, monthly)
        except OpenBIError as exc:
            self.failed.emit(str(exc))
        except Exception as exc:
            self.failed.emit(f"Unexpected error: {exc}")


def _fmt_money(value: float) -> str:
    return f"${value:,.0f}"


def _fmt_int(value: int) -> str:
    return f"{value:,}"


class DashboardView(QWidget):
    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self._config = config
        self._worker: _DashboardWorker | None = None

        self._build_ui()

    # -- UI ---------------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.setSpacing(16)

        # Header row: title + refresh button
        header = QHBoxLayout()
        title = QLabel("Executive Dashboard")
        title.setStyleSheet("font-size: 22px; font-weight: 600;")
        header.addWidget(title)
        header.addStretch(1)

        self._refresh_button = QPushButton("Refresh")
        self._refresh_button.clicked.connect(self.refresh)
        header.addWidget(self._refresh_button)
        outer.addLayout(header)

        # Status line
        self._status = QLabel("")
        self._status.setStyleSheet("color: #666; font-size: 12px;")
        outer.addWidget(self._status)

        # KPI cards row
        cards = QGridLayout()
        cards.setHorizontalSpacing(12)
        cards.setVerticalSpacing(12)

        self._card_revenue = KPICard("Total Revenue")
        self._card_profit = KPICard("Total Profit")
        self._card_orders = KPICard("Orders")
        self._card_margin = KPICard("Profit Margin")

        cards.addWidget(self._card_revenue, 0, 0)
        cards.addWidget(self._card_profit, 0, 1)
        cards.addWidget(self._card_orders, 0, 2)
        cards.addWidget(self._card_margin, 0, 3)
        outer.addLayout(cards)

        # Chart
        chart_label = QLabel("Monthly Revenue")
        chart_label.setStyleSheet("font-size: 16px; font-weight: 600; margin-top: 8px;")
        outer.addWidget(chart_label)

        self._chart = QChart()
        self._chart.setTitle("")
        self._chart.legend().hide()
        self._chart.setBackgroundBrush(QColor("#ffffff"))
        self._chart.setAnimationOptions(QChart.SeriesAnimations)

        self._chart_view = QChartView(self._chart)
        self._chart_view.setRenderHint(QPainter.Antialiasing)
        self._chart_view.setMinimumHeight(300)
        outer.addWidget(self._chart_view, 1)

    # -- data loading -----------------------------------------------------

    def refresh(self) -> None:
        self._refresh_button.setEnabled(False)
        self._status.setText("Loading …")
        self._status.setStyleSheet("color: #666; font-size: 12px;")

        self._worker = _DashboardWorker(self._config.api_url)
        self._worker.succeeded.connect(self._on_success)
        self._worker.failed.connect(self._on_failure)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_success(
        self,
        kpis: ExecutiveKPIs,
        monthly: list[MonthlyRevenuePoint],
    ) -> None:
        self._card_revenue.set_value(_fmt_money(kpis.total_revenue))
        self._card_profit.set_value(
            _fmt_money(kpis.total_profit),
            subtitle=f"Margin {kpis.profit_margin_pct:.2f}%",
        )
        self._card_orders.set_value(
            _fmt_int(kpis.total_orders),
            subtitle=f"Avg ${kpis.avg_order_value:,.2f}",
        )
        self._card_margin.set_value(f"{kpis.profit_margin_pct:.2f}%")

        self._render_chart(monthly)

        self._status.setText(
            f"Loaded {len(monthly)} months • {kpis.total_orders:,} orders total"
        )
        self._status.setStyleSheet("color: #1a7f37; font-size: 12px;")

    def _on_failure(self, message: str) -> None:
        self._status.setText(f"Failed: {message}")
        self._status.setStyleSheet("color: #b00020; font-size: 12px;")

    def _on_finished(self) -> None:
        self._refresh_button.setEnabled(True)

    # -- chart ------------------------------------------------------------

    def _render_chart(self, points: list[MonthlyRevenuePoint]) -> None:
        self._chart.removeAllSeries()
        for axis in list(self._chart.axes()):
            self._chart.removeAxis(axis)

        if not points:
            return

        series = QLineSeries()
        pen = QPen(QColor("#2f80ed"))
        pen.setWidth(2)
        series.setPen(pen)

        max_rev = 0.0
        for i, p in enumerate(points):
            series.append(i, p.revenue)
            max_rev = max(max_rev, p.revenue)

        self._chart.addSeries(series)

        axis_x = QCategoryAxis()
        axis_x.setLabelsPosition(QCategoryAxis.AxisLabelsPositionOnValue)
        # Show every 6th label to avoid clutter
        for i, p in enumerate(points):
            if i % 6 == 0:
                axis_x.append(f"{p.month_name} {p.year}", i)
        axis_x.setRange(0, len(points) - 1)

        axis_y = QValueAxis()
        axis_y.setRange(0, max_rev * 1.15 if max_rev > 0 else 1)
        axis_y.setLabelFormat("$%.0f")

        self._chart.addAxis(axis_x, Qt.AlignBottom)
        self._chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)

    # -- lifecycle --------------------------------------------------------

    def showEvent(self, event) -> None:  # noqa: N802 (Qt override)
        super().showEvent(event)
        # Load data the first time the view is shown.
        if not self._status.text():
            self.refresh()
