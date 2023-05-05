import pyglet  # type: ignore
import datetime
from comps import MusicPlayer
from tinytag import TinyTag  # type: ignore
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import QTimer
from PyQt5 import uic, QtGui
from typing import (
    Iterable,
    Union,
    Any,
)
from .uiactions import (
    get_disk,
    get_lyrics_file,
    set_lyrics_delay,
    mute_setup,
    manual_save_lyrics,
    make_file_types,
    edit_volume,
)
from lyricshandler import (
    Renderer,
)
from actions import (
    FPS,
    LOGO,
    TITLE,
    VERISONS,
    PLAYERUI,
    PAUSE_BTN,
    NEXT_BTN,
    PLAY_BTN,
    MUTE_BTN,
    THEMECLR,
    SHORTCUTS,
    LYRICS_DIR,
    BACKGROUND,
    PREVIOUS_BTN,
    config,
)
from PyQt5.QtWidgets import (
    QLabel,
    QSlider,
    QShortcut,
    QMainWindow,
    QListWidget,
    QPushButton,
    QFileDialog,
    QInputDialog,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        uic.loadUi(PLAYERUI, self)   # type: ignore
        self.window_title = f"{TITLE} {VERISONS[-1]}"
        self.setWindowIcon(QtGui.QIcon(LOGO))
        self.setFixedSize(self.width(), self.height())

        self.player = MusicPlayer(get_disk(config), config.get('is_muted'), config.get('volume'))

        self.set_title()

        self.sound = pyglet.media.Player()
        self.current_song = pyglet.media.load(self.player.disk.song_path)

        self.lyrics = Renderer(get_lyrics_file(LYRICS_DIR, self.player, Renderer.EXTENSION))

        self.sound.queue(self.current_song)

        # Load components
        self._load_sliders()
        self._load_labels()
        self._load_lists()
        self._load_btns()

        # Set UI
        self.play_btn.setIcon(QtGui.QIcon(self.play_btn_switcher()))
        self.current_playing_lbl.setText(self.player.disk.title())
        self.music_container.setCurrentRow(self.player.disk.song_index)
        self.volume_lbl.setText(f"Vol: {self.player.volume}")
        self.volume_bar.setValue(self.player.volume)
        self.volume_bar.setTickPosition(10)
        self.volume_bar.setMaximum(100)
        self._fill_list_widget()

        # Set commands
        self.play_btn.clicked.connect(lambda: self.play_btn_switcher())
        self.music_container.itemDoubleClicked.connect(
            lambda: self.manual_pick(self.music_container)
        )
        self.volume_bar.valueChanged.connect(lambda: self.volume_control())
        self.next_btn.clicked.connect(lambda: self.next_song())
        self.prev_btn.clicked.connect(lambda: self.prev_song())
        self.mute_btn.clicked.connect(lambda: self.mute_player())

        self.is_pressed = False
        self.song_slider.sliderPressed.connect(lambda: self._slider_pressed())
        self.song_slider.sliderReleased.connect(
            lambda: self.move_song(self.song_slider.value() / 60)
        )

        last_song = config.get('last_song')
        if last_song:
            self.move_song(last_song['timestamp'])

        # Key binds
        self.play_shortcut = QShortcut(QKeySequence(SHORTCUTS['PLAY-PAUSE']), self)
        self.next_shortcut = QShortcut(QKeySequence(SHORTCUTS['NEXT SONG']), self)
        self.prev_shortcut = QShortcut(QKeySequence(SHORTCUTS['PREV SONG']), self)
        self.mute_shortcut = QShortcut(QKeySequence(SHORTCUTS['MUTE']), self)

        self.play_shortcut.activated.connect(lambda: self.play_btn_switcher())  # type: ignore
        self.next_shortcut.activated.connect(lambda: self.next_song())  # type: ignore
        self.prev_shortcut.activated.connect(lambda: self.prev_song())  # type: ignore
        self.mute_shortcut.activated.connect(lambda: self.mute_player())  # type: ignore

        # Menu actions
        self.actionChoose_file.triggered.connect(lambda: self.save_lyric_file())
        self.actionCreate.triggered.connect(lambda: print('create'))
        self.actionShortcuts.triggered.connect(lambda: print('shortcuts'))
        self.actionDelay.triggered.connect(lambda: self.set_lyrics_delay())

        # Dynamic updating
        timer = QTimer(self.total_time_lbl)
        timer.timeout.connect(self.update)  # type: ignore
        timer.start(FPS(20))

    def closeEvent(self, event: Any) -> None:
        # When player closes, the current timestamp of
        # the song (- set_behind seconds) is saved
        set_behind = 2
        timestamp = float(f"{self.sound.time:.2f}")
        timestamp -= set_behind
        config.edit('last_song', {'song': self.player.disk.song_mp3, 'timestamp': timestamp})

    def _load_btns(self) -> None:
        self.prev_btn = self.findChild(QPushButton, 'prev_btn')
        self.next_btn = self.findChild(QPushButton, 'next_btn')
        self.play_btn = self.findChild(QPushButton, 'play_btn')
        self.mute_btn = self.findChild(QPushButton, 'mute_btn')

        self.prev_btn.setIcon(QtGui.QIcon(PREVIOUS_BTN))
        self.next_btn.setIcon(QtGui.QIcon(NEXT_BTN))
        self.play_btn.setIcon(QtGui.QIcon(PLAY_BTN))
        self.mute_btn.setIcon(QtGui.QIcon(MUTE_BTN))

        self.prev_btn.setStyleSheet(f'background-color: {THEMECLR}; border-radius: 10%;')
        self.next_btn.setStyleSheet(f'background-color: {THEMECLR}; border-radius: 10%;')
        self.play_btn.setStyleSheet(f'background-color: {THEMECLR}; border-radius: 10%;')
        self.mute_btn.setStyleSheet(f'background-color: {THEMECLR}; border-radius: 10%;')

    def _load_sliders(self) -> None:
        self.song_slider = self.findChild(QSlider, 'music_prog_bar')
        self.volume_bar = self.findChild(QSlider, 'volume_bar')

    def _load_labels(self) -> None:
        self.current_playing_lbl = self.findChild(QLabel, 'current_playing_lbl')
        self.current_time_lbl = self.findChild(QLabel, 'current_time_lbl')
        self.total_time_lbl = self.findChild(QLabel, 'total_time_lbl')
        self.volume_lbl = self.findChild(QLabel, 'volume_lbl')
        self.lyrics_lbl = self.findChild(QLabel, 'lyrics_lbl')
        self.bg_lbl = self.findChild(QLabel, 'bg_lbl')

        self.lyrics_lbl.setStyleSheet(
            'color: white; font-weight: bold;\
            font-size: 20px; background-color: rgba(255, 255, 255, 0);'
        )
        self.bg_lbl.setStyleSheet(f"background-image : url({BACKGROUND})")
        self.current_playing_lbl.setStyleSheet(f'color: {THEMECLR};')
        self.current_time_lbl.setStyleSheet((f'color: {THEMECLR};'))
        self.total_time_lbl.setStyleSheet((f'color: {THEMECLR};'))
        self.volume_lbl.setStyleSheet((f'color: {THEMECLR};'))
        self.current_playing_lbl.setWordWrap(True)

    def _slider_pressed(self) -> None:
        self.is_pressed = True

    def move_song(self, seconds: int) -> None:
        self.is_pressed = False
        self.sound.seek(seconds)

    def _load_lists(self) -> None:
        self.music_container = self.findChild(QListWidget, 'music_container')

        self.music_container.setStyleSheet(
            f"background-color: rgba(255, 255, 255, 0); color: {THEMECLR};"
        )
        self.music_container.setWordWrap(True)
        self.music_container.setSpacing(3)

    def _fill_list_widget(self) -> None:
        for song in self.player.disk:
            self.music_container.addItem(song)
        self.music_container.setCurrentRow(self.player.disk.song_index)

    def set_title(self) -> None:
        if self.player.is_muted:
            self.setWindowTitle(self.window_title + " MUTED")
        else:
            self.setWindowTitle(self.window_title)

    def mute_player(self) -> None:
        mute_setup(self.player, config)
        self.set_title()

    def save_lyric_file(self) -> None:
        try:
            path = self._file_explorer(('srt',))
            manual_save_lyrics(path, self.player, LYRICS_DIR)
        except FileNotFoundError:
            # The file explorer was probably closed
            pass

    def _file_explorer(self, file_types: Iterable[str]) -> str:
        types = make_file_types(file_types)
        path, _ = QFileDialog.getOpenFileName(self, "Choose file", "", types)
        return path

    def display_lyric(self, line: Union[str, None]) -> None:
        if line is not None:
            self.lyrics_lbl.setText(line)
        else:
            self.lyrics_lbl.setText("")

    def update_song(self) -> None:
        self.current_playing_lbl.setText(self.player.disk.title())
        self.music_container.setCurrentRow(self.player.disk.song_index)

        self.sound = pyglet.media.Player()
        self.current_song = pyglet.media.load(self.player.disk.song_path)

        self.lyrics = Renderer(get_lyrics_file(LYRICS_DIR, self.player, Renderer.EXTENSION))

        self.sound.queue(self.current_song)

        self.sound.play() if self.player else self.sound.pause()

    def set_lyrics_delay(self) -> None:
        delay, _ = QInputDialog.getText(self, 'Lyrics delay', 'Set your lyrics delay')
        key = f"{self.player.disk.song_path}.delay"
        set_lyrics_delay(key, delay, config)

    def next_song(self) -> None:
        self.player.disk.next()
        self.update_song()

    def prev_song(self) -> None:
        self.player.disk.prev()
        self.update_song()

    def manual_pick(self, music_container: QListWidget) -> None:
        self.player.disk.user_pick(music_container.currentRow())
        self.update_song()

    def play_btn_switcher(self) -> str:
        self.player.playing()
        img = PAUSE_BTN if self.player else PLAY_BTN

        self.sound.play() if self.player else self.sound.pause()
        self.play_btn.setIcon(QtGui.QIcon(img))
        return img

    def volume_control(self) -> None:
        edit_volume(config, self.player, self.volume_bar.value())

        self.volume_lbl.setText(f"Vol: {self.volume_bar.value()}")
        if not self.player.is_muted:
            self.sound.volume = self.player.volume / 100
        #                                          ^^^^^
        # This is because self.sound.volume accepts
        # values from 0.0 - 1.0 but I want to display 0 - 100
        # Example: displayed = 50; 50 / 100 = 0.5

    def helper_update_slider(self, slider: QSlider, x: int) -> None:
        # # Update slider's position every ms that ellapses
        slider.tracking = True
        slider.setValue(x)
        slider.sliderPosition = x  # type: ignore
        slider.update()
        slider.repaint()

    def update(self) -> None:  # type: ignore
        tag = TinyTag.get(self.player.disk.song_path)
        total_time = tag.duration
        total_seconds = total_time * 60
        self.song_slider.setRange(0, total_seconds)  # Set the total steps of the slider

        # Current time. Use this for the slider update
        current_time = self.sound.time
        current_seconds = current_time * 60

        if not self.is_pressed:
            # When the slider is pressed, stop updating the progres bar automaticaly so we can
            # set it where it will be released
            self.helper_update_slider(self.song_slider, current_seconds)

        if current_time >= total_time:
            self.next_song()

        seconds_to_minute_format = datetime.timedelta(seconds=current_time)
        # total_time_to_minute is used for the slider steps
        total_time_to_minute = str(datetime.timedelta(seconds=total_time))

        if not self.player.is_muted:
            self.volume_control()
        elif self.player.is_muted:
            self.sound.volume = 0

        delay_key = f"{self.player.disk.song_path}.delay"
        lyric_line = self.lyrics.get_line(seconds_to_minute_format, config.get(delay_key))
        self.display_lyric(lyric_line)

        self.total_time_lbl.setText(total_time_to_minute)

        current_time_text = str(seconds_to_minute_format)
        if '.' in current_time_text:
            current_time_text = current_time_text[:current_time_text.index('.') + 3]
            self.current_time_lbl.setText(current_time_text)
