from actions.constants import (
    PAUSE_BTN,
    PLAY_BTN,
)
from comps.musicplayer import MusicPlayer
from PyQt5.QtWidgets import QPushButton
from PyQt5 import QtGui

def play_btn_switcher(player: MusicPlayer, play_btn: QPushButton, testing: bool=False) -> str:
    """Return the state of the player as a string to set the button accordingly

    :param MusicPlayer player: Main MusicPlayerObject
    :param QPushButton play_btn: UI's play button
    :param bool testing: It it's testing environment set to True
    to avoid conflicts with the btn.setText(), defaults to False
    :return str: The current status of the player; True -> Pause / Fasle -> Play
    """    
    img = PLAY_BTN if player else PAUSE_BTN
    if not testing:
        play_btn.setIcon(QtGui.QIcon(img))
    player.play()

    return img


def clear_song_extension(song: str):
    reverse = song[::-1]
    return reverse[reverse.index('.')+1:][::-1]
