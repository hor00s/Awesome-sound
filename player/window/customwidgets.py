from PyQt5 import QtGui
from typing import (
    Any,
)
from PyQt5.QtWidgets import (
    QScrollArea,
    QMessageBox,
    QVBoxLayout,
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
