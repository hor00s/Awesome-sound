import os
import srt
import json
import datetime as dt
from .languages import get_message
from actions import get_active_language
from PyQt5 import QtGui
from actions import (
    PLATFORM,
    PLAY_BTN,
    MUTE_BTN,
    PAUSE_BTN,
    FORBIDDEN_CHARS,
)
from PyQt5.QtCore import (
    Qt,
    QThread,
    QObject,
    QDateTime,
    pyqtSignal,
)
from typing import (
    NamedTuple,
    Generator,
    Iterable,
    Optional,
    Callable,
    Tuple,
    Dict,
    List,
    Any,
)
from .qstyles import (
    lineedit_style,
    status_bar_btn_style,
)
from PyQt5.QtWidgets import (
    QPlainTextEdit,
    QDateTimeEdit,
    QScrollArea,
    QGridLayout,
    QPushButton,
    QMessageBox,
    QVBoxLayout,
    QComboBox,
    QLineEdit,
    QDialog,
    QSlider,
    QWidget,
    QLabel,
)


class CustomLineEdit(QLineEdit):

    def __init__(self, forbidden_chars: Iterable[Any], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.forbidden_chars = forbidden_chars
        if forbidden_chars is not None:
            self.textChanged.connect(lambda: self.validate_input(forbidden_chars))  # type: ignore

    def validate_input(self, forbidden_chars: str) -> None:
        if self.is_valid():
            self.setStyleSheet('')
        else:
            self.setStyleSheet('background-color: red;')

    def is_valid(self) -> bool:
        return not any(char in self.text() for char in self.forbidden_chars)


class RenamePrompt(QDialog):
    def __init__(self, title: str, prompt: str, default_field: str = "",
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.q = False
        self.setWindowTitle(title)

        self.forbidden_chars = FORBIDDEN_CHARS[PLATFORM]

        self.my_layout = QGridLayout(self)
        self.prompt = QLabel(prompt)
        self.name_inp = CustomLineEdit(self.forbidden_chars, self)
        self.ok_btn = QPushButton("Ok")
        self.cancel_btn = QPushButton("Cancel")
        self.name_inp.setText(default_field)

        self.ok_btn.clicked.connect(self.accept)  # type: ignore
        self.cancel_btn.clicked.connect(self.reject)  # type: ignore

        self.my_layout.addWidget(self.prompt, 0, 0, 1, 2)
        self.my_layout.addWidget(self.name_inp, 1, 0, 1, 2)
        self.my_layout.addWidget(self.ok_btn, 2, 0)
        self.my_layout.addWidget(self.cancel_btn, 2, 1)
        self.exec_()

    def accept(self) -> None:
        if self.name_inp.is_valid():
            self.q = True
            return super().accept()

    def reject(self) -> None:
        self.q = False
        return super().reject()

    def get_text(self) -> Tuple[str, bool]:
        return self.name_inp.text(), self.q


class LogsWindow(QMessageBox):
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
        bottom = scroll.verticalScrollBar().maximum()
        scroll.verticalScrollBar().setValue(bottom)


class ShortcutWindow(QMessageBox):
    def __init__(self, title: str, content_lines: List[List[str]], min_width: int,
                 min_height: int, icon: QtGui.QIcon, *args: Any, **kwargs: Any) -> None:
        QMessageBox.__init__(self, *args, **kwargs)
        self.setWindowTitle(title)
        self.setWindowIcon(icon)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        self.content = QWidget()
        scroll.setWidget(self.content)
        lay = QGridLayout(self.content)

        label_style = """
            QLabel {
                font-size: 14px;
                color: #333333;
                background-color: #F0F0F0;
                padding: 5px;
                border: 1px solid #CCCCCC;
            }
        """
        header_style = """
            QLabel {
                font-size: 14px;
                color: #333333;
                background-color: #F0F0F0;
                padding: 5px;
                border: 1px solid #CCCCCC;
                font-weight: bold;
            }
        """

        header_desc = QLabel('Description')
        header_key = QLabel('Key')
        header_desc.setStyleSheet(header_style)
        header_key.setStyleSheet(header_style)

        lay.addWidget(header_desc, 0, 0)
        lay.addWidget(header_key, 0, 1)

        for row, pair in enumerate(content_lines):
            desc, key = pair
            key_lbl = QLabel(desc)
            name_lbl = QLabel(key)
            key_lbl.setStyleSheet(label_style)
            name_lbl.setStyleSheet(label_style)
            lay.addWidget(key_lbl, row + 1, 0)
            lay.addWidget(name_lbl, row + 1, 1)

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


class WorkerThread(QThread):
    finished = pyqtSignal()  # type: ignore

    def __init__(self, parent: QObject, func: Callable[..., Any],
                 *args: Any, **kwargs: Any) -> None:
        super().__init__(parent)
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self) -> None:
        self.func(*self.args, **self.kwargs)
        self.finished.emit()  # type: ignore


class State(NamedTuple):
    name: str
    datetime: str
    playback: bool
    mute: bool
    volume: int
    applied: bool


class ActionsWindow(QDialog):
    # TODO: Docstrings
    def __init__(self, parent: QWidget, actions_dir: str) -> None:
        super().__init__(parent)
        self._current_actions: Dict[str, State] = {}
        self._actions_dir = actions_dir
        self._actions_buffer = self.buf_actions()

        self._accepted = False
        self._mute_state = False
        self._playback_state = False

    def set_up(self, title: str) -> None:
        self.setWindowTitle(title)
        self.my_layout = QGridLayout()
        self.setFixedWidth(200)

        self.forbidden_chars = FORBIDDEN_CHARS[PLATFORM]
        self.action_name = CustomLineEdit(self.forbidden_chars, self)

        self.dtedit = QDateTimeEdit(self)
        self.dtedit.setDateTime(dt.datetime.now())
        self.dtedit.setDisplayFormat('yyyy-MM-dd hh:mm')

        self.play_btn = QPushButton(self)
        self.pause_btn = QPushButton(self)
        self.mute_btn = QPushButton(self)
        self.vol_slider = QSlider(Qt.Horizontal, self)  # type: ignore
        self.vol_lbl = QLabel(self)

        self.play_btn.setIcon(QtGui.QIcon(PLAY_BTN))
        self.pause_btn.setIcon(QtGui.QIcon(PAUSE_BTN))
        self.mute_btn.setIcon(QtGui.QIcon(MUTE_BTN))

        self.vol_slider.setMaximum(100)
        self.vol_lbl.setText(str(self.vol_slider.value()))

        self.load_action_btn = QPushButton(self)
        self.delete_action_btn = QPushButton(self)
        self.load_action_btn.setText('Load')
        self.delete_action_btn.setText('Delete')

        self.actions_box = QComboBox(self)

        self.save_btn = QPushButton(self)
        self.save_btn.setText('Save action')

        self.set_playback_state(False)
        self.vol_slider.setValue(50)
        self.set_volume()

        self.mute_btn.clicked.connect(  # type: ignore
            lambda: self.set_mute_state(not self._mute_state)
        )
        self.play_btn.clicked.connect(lambda: self.set_playback_state(True))  # type: ignore
        self.pause_btn.clicked.connect(lambda: self.set_playback_state(False))  # type: ignore
        self.vol_slider.valueChanged.connect(lambda: self.set_volume())  # type: ignore
        self.save_btn.clicked.connect(lambda: self.finish())  # type: ignore
        self.load_action_btn.clicked.connect(lambda: self.edit())  # type: ignore
        self.delete_action_btn.clicked.connect(lambda: self.delete())  # type: ignore

        self.setLayout(self.my_layout)
        self.my_layout.addWidget(self.action_name, 0, 0, 1, 2)
        self.my_layout.addWidget(self.dtedit, 1, 0, 1, 2)
        self.my_layout.addWidget(self.play_btn, 2, 0)
        self.my_layout.addWidget(self.pause_btn, 2, 1)
        self.my_layout.addWidget(self.mute_btn, 3, 0, 1, 2)
        self.my_layout.addWidget(self.vol_slider, 4, 0, 1, 2)
        self.my_layout.addWidget(self.vol_lbl, 5, 0, 1, 2)
        self.my_layout.addWidget(self.load_action_btn, 6, 0)
        self.my_layout.addWidget(self.delete_action_btn, 6, 1)
        self.my_layout.addWidget(self.actions_box, 7, 0, 1, 2)
        self.my_layout.addWidget(self.save_btn, 8, 0, 1, 2)

        self.display()
        self.edit()

        self.exec_()

    def closeEvent(self, a0: Any) -> None:
        self._accepted = False
        self.reject()
        super().closeEvent(a0)

    def finish(self) -> None:
        if self.action_name.text() and self.action_name.is_valid():
            self._accepted = True
            self.accept()

    def accepted(self) -> bool:  # type: ignore
        return self._accepted

    def set_playback_state(self, state: bool) -> None:
        self._playback_state = state
        if self._playback_state:
            self.play_btn.setStyleSheet('background-color: green;')
            self.pause_btn.setStyleSheet('')
        elif not self._playback_state:
            self.play_btn.setStyleSheet('')
            self.pause_btn.setStyleSheet('background-color: green;')

    def set_mute_state(self, state: bool) -> None:
        self._mute_state = state
        if self._mute_state:
            self.mute_btn.setStyleSheet('background-color: green;')
        elif not self._mute_state:
            self.mute_btn.setStyleSheet('')

    def set_volume(self) -> None:
        self.vol_lbl.setText(str(self.vol_slider.value()))

    @staticmethod
    def string_to_dt(datetime: str) -> dt.datetime:
        return dt.datetime.strptime(datetime, '%Y-%m-%d %H:%M')

    @staticmethod
    def dt_to_action_dt(datetime: dt.datetime) -> dt.datetime:
        time = f"{datetime.year}-{datetime.month}-{datetime.day} {datetime.hour}:{datetime.minute}"
        return ActionsWindow.string_to_dt(time)

    @staticmethod
    def qtdate_to_string(datetime: QDateTime) -> str:
        date = datetime.date()
        time = datetime.time()
        return f"{date.year()}-{date.month()}-{date.day()} {time.hour()}:{time.minute()}"

    def _save(self, state: State) -> None:
        name = self.action_name.text()
        file = f"{name}.json"
        path = os.path.join(self._actions_dir, file)
        with open(path, mode='w') as f:
            json.dump(state, f)
        self._actions_buffer = self.buf_actions()

    def mark_applied(self, state: State) -> None:
        name = state.name
        file = f"{name}.json"
        path = os.path.join(self._actions_dir, file)
        with open(path, mode='r') as f:
            state = State(*json.load(f))
        new_state = State(state.name, state.datetime, state.playback,
                          state.mute, state.volume, applied=True)
        with open(path, mode='w') as f:
            json.dump(list(new_state), f)

    def delete(self) -> None:
        name = self.action_name.text()
        file = f"{name}.json"
        path = os.path.join(self._actions_dir, file)
        os.remove(path)
        self._actions_buffer = self.buf_actions()
        self.display()
        self.edit()

    def save(self) -> State:
        name = self.action_name.text()

        datetime = self.qtdate_to_string(self.dtedit.dateTime())
        pb = self._playback_state
        mute = self._mute_state
        vol = self.vol_slider.value()

        state = State(name, datetime, pb, mute, vol, applied=False)
        self._save(state)
        return state

    def buf_actions(self) -> List[State]:
        """Load all the saved actions in memmory so we don't
        have to always go and re-read them

        :return:
        :rtype: List[State]
        """
        actions = []
        for file in os.listdir(self._actions_dir):
            path = os.path.join(self._actions_dir, file)
            with open(path, mode='r') as f:
                state = State(*json.load(f))
            actions.append(state)
        return actions

    def display(self) -> None:
        self.actions_box.clear()
        for action in self._actions_buffer:
            name = action.name
            self.actions_box.addItem(name)

    def edit(self) -> None:
        name = self.actions_box.currentText()
        if name:
            file = f"{name}.json"
            path = os.path.join(self._actions_dir, file)
            with open(path, mode='r') as f:
                state = State(*json.load(f))

            self.action_name.setText(state.name)
            self.dtedit.setDateTime(ActionsWindow.string_to_dt(state.datetime))
            self.set_playback_state(state.playback)
            self.set_mute_state(state.mute)
            self.vol_slider.setValue(state.volume)

    def get(self) -> Generator[State, Any, None]:
        yield from self._actions_buffer
