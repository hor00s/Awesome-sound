from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from typing import (
    Optional,
    Any,
)
from .qstyles import (
    lineedit_style,
    status_bar_btn_style,
)
from PyQt5.QtWidgets import (
    QScrollArea,
    QPushButton,
    QMessageBox,
    QVBoxLayout,
    QLineEdit,
    QWidget,
    QLabel,
)


class ScrollMessageBox(QMessageBox):
    def __init__(self, title: str, content_lines: str, min_width: int,
                 min_height: int, icon: QtGui.QIcon, *args: Any, **kwargs: Any) -> None:
        QMessageBox.__init__(self, *args, **kwargs)
        self.setWindowTitle(title)
        self.setWindowIcon(icon)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        self.content = QWidget()
        scroll.setWidget(self.content)
        lay = QVBoxLayout(self.content)

        lay.addWidget(QLabel(content_lines, self))

        self.layout().addWidget(scroll, 0, 0, 1, self.layout().columnCount())  # type: ignore
        self.setStyleSheet("QScrollArea{min-width:%spx; min-height: %spx}"
                           % (str(min_width), str(min_height)))


class StatusBarButton(QPushButton):
    def __init__(self, parent: Optional[QWidget] = None, text: str = "",
                 stylesheet: str = status_bar_btn_style, tooltip_text: Optional[str] = None):
        super().__init__(parent=parent)
        self.setStyleSheet(stylesheet)
        self.setText(text)
        self.setCursor(Qt.PointingHandCursor)  # type: ignore
        if tooltip_text is not None:
            self.setToolTip(tooltip_text)


class StatusBarTimeEdit(QLineEdit):
    def __init__(self, parent: Optional[QWidget] = None, text: str = "",
                 stylesheet: str = lineedit_style):
        super().__init__(parent=parent)
        self.setStyleSheet(stylesheet)
        self.setText(text)
