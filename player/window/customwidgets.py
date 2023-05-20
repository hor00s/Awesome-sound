import srt
from .languages import get_message
from actions import get_active_language
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from typing import (
    Optional,
    Tuple,
    Any,
)
from .qstyles import (
    lineedit_style,
    status_bar_btn_style,
)
from PyQt5.QtWidgets import (
    QPlainTextEdit,
    QScrollArea,
    QPushButton,
    QMessageBox,
    QVBoxLayout,
    QComboBox,
    QLineEdit,
    QDialog,
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


class ComboboxDialog(QDialog):
    def __init__(self, parent: QWidget, title: str, text: str,
                 *options: Any, width: int = 300, height: int = 300) -> None:
        super().__init__(parent)
        self._r_value = (False, '')

        layout = QVBoxLayout()
        self.setWindowTitle(title)
        label = QLabel(self)
        label.setText(text)
        layout.addWidget(label)

        self.combobox = QComboBox(parent)
        for option in options:
            self.combobox.addItem(option)
        layout.addWidget(self.combobox)
        button_ok = QPushButton()
        button_cancel = QPushButton()
        button_ok.setText('Ok')
        button_cancel.setText('Cancel')

        button_ok.clicked.connect(self.ok)  # type: ignore
        button_cancel.clicked.connect(self.cancel)  # type: ignore

        layout.addWidget(button_ok)
        layout.addWidget(button_cancel)
        self.setLayout(layout)
        self.setFixedWidth(width)
        self.setFixedHeight(height)
        self.exec_()

    def get_option(self) -> Tuple[bool, str]:
        self.accept()
        return self._r_value

    def ok(self) -> None:
        value = self.combobox.currentText()
        self.accept()
        self._r_value = (True, value)

    def cancel(self) -> None:
        self.reject()
        self._r_value = (False, '')

    def closeEvent(self, a0: Any) -> None:
        self.cancel()


class TextEditor(QDialog):
    def __init__(self, parent: QWidget, title: str, prompt: str, text: str = ""):
        super().__init__(parent)
        self._r_value = (False, '')

        layout = QVBoxLayout()
        self.setWindowTitle(title)
        prompt_lbl = QLabel(self)
        prompt_lbl.setText(prompt)

        self.error_lbl = QLabel(self)

        self.textarea = QPlainTextEdit(self)
        self.textarea.setPlainText(text)

        save_btn = QPushButton(self)
        save_btn.setText('Save')
        cancel_btn = QPushButton(self)
        cancel_btn.setText('Cancel')

        cancel_btn.clicked.connect(self.reject)  # type: ignore
        save_btn.clicked.connect(self.accept)  # type: ignore

        layout.addWidget(prompt_lbl)
        layout.addWidget(self.textarea)
        layout.addWidget(save_btn)
        layout.addWidget(cancel_btn)
        layout.addWidget(self.error_lbl)

        self.setLayout(layout)
        self.exec_()

    def closeEvent(self, a0: Any) -> None:
        self.reject()

    def accept(self) -> None:
        self._r_value = True, self.textarea.toPlainText()
        _, lyrics = self._r_value
        try:
            tuple(srt.parse(lyrics))
        except srt.SRTParseError:
            lang = get_active_language()
            msg = get_message(lang, 'general_error')
            self.error_lbl.setText(msg)
        else:
            super().accept()

    def reject(self) -> None:
        self._r_value = False, ''
        super().reject()

    def accepted(self) -> bool:  # type: ignore
        v, _ = self._r_value
        return v

    def save(self, path: str) -> None:
        _, text = self._r_value
        with open(path, mode='w') as f:
            f.write(text)

    def get_text(self) -> str:
        _, text = self._r_value
        return text
