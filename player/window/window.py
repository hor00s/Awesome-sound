import os
import pyglet
import datetime
from typing import Union
from tinytag import TinyTag
from comps.song import Song
from comps.musicplayer import MusicPlayer
from lyricshandler.creator import Creator
from lyricshandler.renderer import Renderer
from actions.constants import (
    FPS,
    LOGO,
    TITLE,
    VERISONS,
    PLAYERUI,
    NEXT_BTN,
    PLAY_BTN,
    THEMECLR,
    SONGSFILE,
    SHORTCUTS,
    LYRICS_DIR,
    BACKGROUND,
    PREVIOUS_BTN,
)
from actions.actions import (
    play_btn_switcher,
    clear_song_extension,
)
from PyQt5.QtWidgets import (
    QLabel,
    QSlider,
    QShortcut,
    QMainWindow,
    QListWidget,
    QPushButton,
    QFileDialog,
    QApplication,
)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import QTimer
from PyQt5 import uic, QtGui

# self.sound.position -> Somethong
# self.sound.time -> Get total played of a sound
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi(PLAYERUI, self)
        self.setWindowTitle(f"{TITLE} {VERISONS[-1]}")
        self.setWindowIcon(QtGui.QIcon(LOGO))
        self.setFixedSize(self.width(), self.height())

        self.player = MusicPlayer(Song(SONGSFILE))

        self.sound = pyglet.media.Player()
        self.current_song = pyglet.media.load(self.player.song.current_song_as_file)

        song_lyrics = self._get_lyrics_file()
        self.lyrics = Renderer(song_lyrics)

        self.sound.queue(self.current_song)

        # Load components
        self._load_sliders()
        self._load_labels()
        self._load_lists()
        self._load_btns()
        
        # Set UI
        self.play_btn.setIcon(QtGui.QIcon(play_btn_switcher(self.player, self.play_btn, self.sound)))
        self.current_playing_lbl.setText(clear_song_extension(self.player.song.current_song))
        self.music_container.setCurrentRow(self.player.song.song_index)
        self.volume_lbl.setText(f"Vol: {self.player.volume}")
        self.volume_bar.setValue(self.player.volume)
        self.volume_bar.setTickPosition(10)
        self.volume_bar.setMaximum(100)
        self._fill_list_widget()

        # Set commands
        self.play_btn.clicked.connect(lambda: play_btn_switcher(self.player, self.play_btn, self.sound))
        self.music_container.itemDoubleClicked.connect(lambda: self.manual_pick(self.music_container))
        self.volume_bar.valueChanged.connect(lambda: self.volume_control())
        self.next_btn.clicked.connect(lambda: self.next_song())
        self.prev_btn.clicked.connect(lambda: self.prev_song())

        self.is_pressed = False
        self.music_prog_bar.sliderPressed.connect(lambda: self._slider_pressed())
        self.music_prog_bar.sliderReleased.connect(lambda: self._slider_release())

        # Key binds
        self.play_shortcut = QShortcut(QKeySequence(SHORTCUTS['PLAY-PAUSE']), self)
        self.next_shortcut = QShortcut(QKeySequence(SHORTCUTS['NEXT SONG']), self)
        self.prev_shortcut = QShortcut(QKeySequence(SHORTCUTS['PREV SONG']), self)

        self.play_shortcut.activated.connect(lambda: play_btn_switcher(self.player, self.play_btn, self.sound))
        self.next_shortcut.activated.connect(lambda: self.next_song())
        self.prev_shortcut.activated.connect(lambda: self.prev_song())

        # Menu actions
        self.actionChoose_file.triggered.connect(lambda: self.manual_pick_lyrics())
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
        self.music_prog_bar = self.findChild(QSlider, 'music_prog_bar')
        self.volume_bar = self.findChild(QSlider, 'volume_bar')

    def _load_labels(self):
        self.current_playing_lbl = self.findChild(QLabel, 'current_playing_lbl')
        self.current_time_lbl = self.findChild(QLabel, 'current_time_lbl')
        self.total_time_lbl = self.findChild(QLabel, 'total_time_lbl')
        self.volume_lbl = self.findChild(QLabel, 'volume_lbl')
        self.lyrics_lbl = self.findChild(QLabel, 'lyrics_lbl')
        self.bg_lbl = self.findChild(QLabel, 'bg_lbl')

        self.lyrics_lbl.setStyleSheet('color: white; font-weight: bold; font-size: 20px; background-color: rgba(255, 255, 255, 0);')
        self.bg_lbl.setStyleSheet(f"background-image : url({BACKGROUND})")
        self.current_playing_lbl.setStyleSheet(f'color: {THEMECLR};')
        self.current_time_lbl.setStyleSheet((f'color: {THEMECLR};'))
        self.total_time_lbl.setStyleSheet((f'color: {THEMECLR};'))
        self.volume_lbl.setStyleSheet((f'color: {THEMECLR};'))
        self.current_playing_lbl.setWordWrap(True)

    def _get_lyrics_file(self):
        lyrics_file = os.path.join(LYRICS_DIR, self.player.song.without_extension() + Renderer.EXTENSION)
        if not os.path.exists(lyrics_file):
            lyrics_file = os.path.join(LYRICS_DIR, 'fake.srt')
            with open(lyrics_file, mode='w') as f:
                f.write("1\n00:00:00,000 --> 00:25:00,000\n")

        return lyrics_file

    def _slider_pressed(self):
        self.is_pressed = True

    def _slider_release(self):
        self.is_pressed = False
        position = self.music_prog_bar.value()
        self.sound.seek(position / 60)

    def _load_lists(self):
        self.music_container = self.findChild(QListWidget, 'music_container')

        self.music_container.setStyleSheet(f"background-color: rgba(255, 255, 255, 0); color: {THEMECLR};")
        self.music_container.setWordWrap(True)
        self.music_container.setSpacing(3)

    def _fill_list_widget(self):
        for song in self.player.song:
            self.music_container.addItem(song) #.addItem(clear_song_extension(song))
            # Choose if a song will be displayed with its
            # extension inside the list widget 
        self.music_container.setCurrentRow(0)

    def manual_pick_lyrics(self):
        path = self._file_explorer()
        creator = Creator(self.player.song, LYRICS_DIR)
        creator.manual_save(path)

    def _file_explorer(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choose file", "", "Srt files (*.srt)")
        return path

    def display_lyric(self, line: Union[str, None]):
        if line is not None:
            self.lyrics_lbl.setText(line)

    def update_song(self):
        self.current_playing_lbl.setText(clear_song_extension(self.player.song.current_song))
        self.music_container.setCurrentRow(self.player.song.song_index)

        self.sound = pyglet.media.Player()
        self.current_song = pyglet.media.load(self.player.song.current_song_as_file)

        song_lyrics = self._get_lyrics_file()
        self.lyrics = Renderer(song_lyrics)

        self.sound.queue(self.current_song)

        self.sound.play() if self.player else self.sound.pause()

    def next_song(self):
        self.player.song.next()
        self.update_song()

    def prev_song(self):
        self.player.song.prev()
        self.update_song()

    def manual_pick(self, music_container: QListWidget):
        self.player.song.user_pick(music_container.currentRow()) 
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
        slider.tracking = True
        slider.setValue(x)
        slider.sliderPosition = x
        slider.update()
        slider.repaint()

    def update(self):
        tag = TinyTag.get(self.player.song.current_song_as_file)
        total_time = tag.duration
        total_seconds = total_time * 60
        self.music_prog_bar.setRange(0, total_seconds) # Set the total steps of the slider

        # Current time. Use this for the slider update
        current_time = self.sound.time
        current_seconds = current_time * 60

        if not self.is_pressed:
            # When the slider is pressed, stop updating the progres bar automaticaly so we can
            # set it where it will be released
            self.helper_update_slider(self.music_prog_bar, current_seconds) # Update slider's position every ms that ellapses

        if current_time >= total_time:
            self.next_song()

        seconds_to_minute_format = datetime.timedelta(seconds=current_time)
        total_time_to_minute = str(datetime.timedelta(seconds=total_time))  # This is used for the slider steps

        lyric_line = self.lyrics.get_line(seconds_to_minute_format)
        self.display_lyric(lyric_line)

        self.total_time_lbl.setText(total_time_to_minute)

        current_time_text = str(seconds_to_minute_format)
        if '.' in current_time_text:
            current_time_text = current_time_text[:current_time_text.index('.') + 3]
            self.current_time_lbl.setText(current_time_text)
