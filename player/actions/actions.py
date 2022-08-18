from pyglet.media.player import Player
from actions.constants import (
    PAUSE_BTN,
    PLAY_BTN,
)
from comps.musicplayer import MusicPlayer
from PyQt5.QtWidgets import QPushButton
from PyQt5 import QtGui


def play_btn_switcher(player: MusicPlayer, play_btn: QPushButton, sound: Player, testing: bool=False) -> str:
    """Return the state of the player as a string to set the button accordingly

    :param MusicPlayer player: Main MusicPlayerObject
    :param QPushButton play_btn: UI's play button
    :param bool testing: It it's testing environment set to True
    to avoid conflicts with the btn.setText(), defaults to False
    :return str: The current status of the player; True -> Pause / Fasle -> Play
    """    
    player.play()
    img = PAUSE_BTN if player else PLAY_BTN
    if not testing:
        sound.play() if player else sound.pause()
        play_btn.setIcon(QtGui.QIcon(img))

    return img


def clear_song_extension(song: str):
    reverse = song[::-1]
    return reverse[reverse.index('.')+1:][::-1]
