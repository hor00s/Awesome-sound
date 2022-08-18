import pyglet
from comps.song import Song
from comps.musicplayer import MusicPlayer
from actions.constants import (
    LOGO,
    TITLE,
    WIDTH,
    HEIGHT,
    VERISONS,
    PLAYERUI,
    NEXT_BTN,
    PLAY_BTN,
    THEMECLR,
    SONGSFILE,
    SHORTCUTS,
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
    QApplication,
)
from PyQt5.QtGui import QKeySequence
from PyQt5 import uic, QtGui

# self.sound.time -> Get total played of a sound
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi(PLAYERUI, self)
        self.setWindowTitle(f"{TITLE} {VERISONS[-1]}")
        self.setWindowIcon(QtGui.QIcon(LOGO))
        self.setFixedSize(WIDTH, HEIGHT)

        self.player = MusicPlayer(Song(SONGSFILE))
        self.sound = pyglet.media.Player()
        self.current_song = pyglet.media.load(self.player.song.current_song_as_file)
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
        self.volume_lbl.setText(f"Vol: {self.volume_bar.value()}")
        self.volume_bar.setValue(self.player.volume)
        self.volume_bar.setTickPosition(10)
        self.volume_bar.setMaximum(100)
        self._fill_list_widget()

        # Set commands
        self.music_container.itemDoubleClicked.connect(lambda: self.manual_pick(self.music_container))
        self.play_btn.clicked.connect(lambda: play_btn_switcher(self.player, self.play_btn, self.sound))
        self.volume_bar.valueChanged.connect(lambda: self.volume_control())
        self.next_btn.clicked.connect(lambda: self.next_song())
        self.prev_btn.clicked.connect(lambda: self.prev_song())

        # Key binds
        self.play_shortcut = QShortcut(QKeySequence(SHORTCUTS['PLAY-PAUSE']), self)
        self.next_shortcut = QShortcut(QKeySequence(SHORTCUTS['NEXT SONG']), self)
        self.prev_shortcut = QShortcut(QKeySequence(SHORTCUTS['PREV SONG']), self)

        self.play_shortcut.activated.connect(lambda: play_btn_switcher(self.player, self.play_btn, self.sound))
        self.next_shortcut.activated.connect(lambda: self.next_song())
        self.prev_shortcut.activated.connect(lambda: self.prev_song())

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
        self.bg_lbl = self.findChild(QLabel, 'bg_lbl')

        self.bg_lbl.setStyleSheet(f"background-image : url({BACKGROUND})")
        self.current_playing_lbl.setStyleSheet(f'color: {THEMECLR};')
        self.current_time_lbl.setStyleSheet((f'color: {THEMECLR};'))
        self.total_time_lbl.setStyleSheet((f'color: {THEMECLR};'))
        self.volume_lbl.setStyleSheet((f'color: {THEMECLR};'))
        self.current_playing_lbl.setWordWrap(True)

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

    def update_song(self):
        self.music_container.setCurrentRow(self.player.song.song_index)
        self.current_playing_lbl.setText(clear_song_extension(self.player.song.current_song))

        self.sound = pyglet.media.Player()
        self.current_song = pyglet.media.load(self.player.song.current_song_as_file)
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
