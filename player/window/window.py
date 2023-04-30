import os
import pyglet
import datetime
from tinytag import TinyTag
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import QTimer
from PyQt5 import uic, QtGui
from typing import (
    Iterable,
    Union,
)
from lyricshandler import (
    Creator,
    Renderer,
)
from comps import (
    MusicPlayer,
    Disk,
)
from actions import (
    FPS,
    LOGO,
    TITLE,
    VERISONS,
    PLAYERUI,
    NEXT_BTN,
    PLAY_BTN,
    THEMECLR,
    SONGSLIST,
    SHORTCUTS,
    LYRICS_DIR,
    BACKGROUND,
    PREVIOUS_BTN,
    play_btn_switcher,
)
from PyQt5.QtWidgets import (
    QLabel,
    QSlider,
    QShortcut,
    QMainWindow,
    QListWidget,
    QPushButton,
    QFileDialog,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi(PLAYERUI, self)
        self.setWindowTitle(f"{TITLE} {VERISONS[-1]}")
        self.setWindowIcon(QtGui.QIcon(LOGO))
        self.setFixedSize(self.width(), self.height())

        self.player = MusicPlayer(Disk(SONGSLIST))

        self.sound = pyglet.media.Player()
        self.current_song = pyglet.media.load(self.player.disk.song)

        self.lyrics = Renderer(self._get_lyrics_file())

        self.sound.queue(self.current_song)

        # Load components
        self._load_sliders()
        self._load_labels()
        self._load_lists()
        self._load_btns()

        # Set UI
        self.play_btn.setIcon(QtGui.QIcon(
            play_btn_switcher(self.player, self.play_btn, self.sound))
        )
        self.current_playing_lbl.setText(self.player.disk.title())
        self.music_container.setCurrentRow(self.player.disk.song_index)
        self.volume_lbl.setText(f"Vol: {self.player.volume}")
        self.volume_bar.setValue(self.player.volume)
        self.volume_bar.setTickPosition(10)
        self.volume_bar.setMaximum(100)
        self._fill_list_widget()

        # Set commands
        self.play_btn.clicked.connect(
            lambda: play_btn_switcher(self.player, self.play_btn, self.sound)
        )
        self.music_container.itemDoubleClicked.connect(
            lambda: self.manual_pick(self.music_container)
        )
        self.volume_bar.valueChanged.connect(lambda: self.volume_control())
        self.next_btn.clicked.connect(lambda: self.next_song())
        self.prev_btn.clicked.connect(lambda: self.prev_song())

        self.is_pressed = False
        self.song_slider.sliderPressed.connect(lambda: self._slider_pressed())
        self.song_slider.sliderReleased.connect(lambda: self._slider_release())

        # Key binds
        self.play_shortcut = QShortcut(QKeySequence(SHORTCUTS['PLAY-PAUSE']), self)
        self.next_shortcut = QShortcut(QKeySequence(SHORTCUTS['NEXT SONG']), self)
        self.prev_shortcut = QShortcut(QKeySequence(SHORTCUTS['PREV SONG']), self)

        self.play_shortcut.activated.connect(
            lambda: play_btn_switcher(self.player, self.play_btn, self.sound)
        )
        self.next_shortcut.activated.connect(lambda: self.next_song())
        self.prev_shortcut.activated.connect(lambda: self.prev_song())

        # Menu actions
        self.actionChoose_file.triggered.connect(lambda: self.save_lyric_file())
        self.actionCreate.triggered.connect(lambda: print('create'))
        self.actionShortcuts.triggered.connect(lambda: print('shortcuts'))

        # Dynamic updating
        timer = QTimer(self.total_time_lbl)
        timer.timeout.connect(self.update)
        timer.start(FPS(20))

    def _load_btns(self):
        self.prev_btn = self.findChild(QPushButton, 'prev_btn')
        self.next_btn = self.findChild(QPushButton, 'next_btn')
        self.play_btn = self.findChild(QPushButton, 'play_btn')

        self.prev_btn.setIcon(QtGui.QIcon(PREVIOUS_BTN))
        self.next_btn.setIcon(QtGui.QIcon(NEXT_BTN))
        self.play_btn.setIcon(QtGui.QIcon(PLAY_BTN))

        self.prev_btn.setStyleSheet(f'background-color: {THEMECLR}; border-radius: 10%;')
        self.next_btn.setStyleSheet(f'background-color: {THEMECLR}; border-radius: 10%;')
        self.play_btn.setStyleSheet(f'background-color: {THEMECLR}; border-radius: 10%;')

    def _load_sliders(self):
        self.song_slider = self.findChild(QSlider, 'music_prog_bar')
        self.volume_bar = self.findChild(QSlider, 'volume_bar')

    def _load_labels(self):
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

    def _get_lyrics_file(self):
        sound_to_srt = self.player.disk.title() + Renderer.EXTENSION
        lyrics_file = os.path.join(LYRICS_DIR, sound_to_srt)

        if not os.path.exists(lyrics_file):
            lyrics_file = os.path.join(LYRICS_DIR, 'fake.srt')
            with open(lyrics_file, mode='w') as f:
                f.write("1\n00:00:00,000 --> 00:25:00,000\n")

        return lyrics_file

    def _slider_pressed(self):
        self.is_pressed = True

    def _slider_release(self):
        self.is_pressed = False
        position = self.song_slider.value()
        self.sound.seek(position / 60)

    def _load_lists(self):
        self.music_container = self.findChild(QListWidget, 'music_container')

        self.music_container.setStyleSheet(
            f"background-color: rgba(255, 255, 255, 0); color: {THEMECLR};"
        )
        self.music_container.setWordWrap(True)
        self.music_container.setSpacing(3)

    def _fill_list_widget(self):
        for song in self.player.disk:
            self.music_container.addItem(song)
        self.music_container.setCurrentRow(0)

    def save_lyric_file(self):
        try:
            path = self._file_explorer(('srt',))
            creator = Creator(self.player.disk, LYRICS_DIR)
            creator.manual_save(path)
        except FileNotFoundError:
            # The file explorer was probably closed
            pass

    def _file_explorer(self, file_types: Iterable[str]):
        types = ""
        for type_ in file_types:
            name = f"{type_.title()} files"
            ext = f"(*.{type_})"
            field = f"{name} {ext};;"
            types += field

        path, _ = QFileDialog.getOpenFileName(self, "Choose file", "", types)
        return path

    def display_lyric(self, line: Union[str, None]):
        if line is not None:
            self.lyrics_lbl.setText(line)
        else:
            self.lyrics_lbl.setText("")

    def update_song(self):
        self.current_playing_lbl.setText(self.player.disk.title())
        self.music_container.setCurrentRow(self.player.disk.song_index)

        self.sound = pyglet.media.Player()
        self.current_song = pyglet.media.load(self.player.disk.song)

        self.lyrics = Renderer(self._get_lyrics_file())

        self.sound.queue(self.current_song)

        self.sound.play() if self.player else self.sound.pause()

    def next_song(self):
        self.player.disk.next()
        self.update_song()

    def prev_song(self):
        self.player.disk.prev()
        self.update_song()

    def manual_pick(self, music_container: QListWidget):
        self.player.disk.user_pick(music_container.currentRow())
        self.update_song()

    def volume_control(self):
        self.player.set_volume(self.volume_bar.value())
        self.volume_lbl.setText(f"Vol: {self.volume_bar.value()}")
        self.sound.volume = self.player.volume / 100
        #                                      ^^^^^
        # This is because self.sound.volume accepts
        # values from 0.0 - 1.0 but I want to display 0 - 100
        # Example: displayed = 50; 50 / 100 = 0.5

    def helper_update_slider(self, slider: QSlider, x: int):
        # # Update slider's position every ms that ellapses
        slider.tracking = True
        slider.setValue(x)
        slider.sliderPosition = x
        slider.update()
        slider.repaint()

    def update(self):
        tag = TinyTag.get(self.player.disk.song)
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

        lyric_line = self.lyrics.get_line(seconds_to_minute_format)
        self.display_lyric(lyric_line)

        self.total_time_lbl.setText(total_time_to_minute)

        current_time_text = str(seconds_to_minute_format)
        if '.' in current_time_text:
            current_time_text = current_time_text[:current_time_text.index('.') + 3]
            self.current_time_lbl.setText(current_time_text)
