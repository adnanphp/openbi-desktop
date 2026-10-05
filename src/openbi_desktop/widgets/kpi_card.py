"""Reusable KPI card widget."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class KPICard(QFrame):
    """A small card showing a label, a large value, and an optional subtitle."""

    def __init__(self, label: str, value: str = "—", subtitle: str = "") -> None:
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(
            "KPICard {"
            "  background: #ffffff;"
            "  border: 1px solid #e0e0e0;"
            "  border-radius: 8px;"
            "}"
        )
        self.setMinimumHeight(110)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(4)

        self._label = QLabel(label.upper())
        self._label.setStyleSheet(
            "color: #888; font-size: 11px; letter-spacing: 1px; font-weight: 600;"
        )
        layout.addWidget(self._label)

        self._value = QLabel(value)
        self._value.setStyleSheet(
            "color: #1f2430; font-size: 26px; font-weight: 700;"
        )
        layout.addWidget(self._value)

        self._subtitle = QLabel(subtitle)
        self._subtitle.setStyleSheet("color: #999; font-size: 11px;")
        self._subtitle.setAlignment(Qt.AlignLeft)
        layout.addWidget(self._subtitle)

        layout.addStretch(1)

    def set_value(self, value: str, subtitle: str = "") -> None:
        self._value.setText(value)
        self._subtitle.setText(subtitle)
