import os
from typing import Callable

to_fps = Callable[[int], int]

SONGSFILE:    tuple[str] = tuple(filter(lambda i: i != '.gitignore', os.listdir('songs')))
PREVIOUS_BTN: str        = os.path.join('images', 'previous-button.png')
PAUSE_BTN:    str        = os.path.join('images', 'pause-button.png')
PLAY_BTN:     str        = os.path.join('images', 'play-button.png')
NEXT_BTN:     str        = os.path.join('images', 'next-button.png')
BACKGROUND:   str        = os.path.join('images', 'background.png')
LOGO:         str        = os.path.join('images', 'applogo.png')
PLAYERUI:     str        = os.path.join('window', 'player.ui')
FPS:          to_fps     = lambda frame_rate: int(1000 / frame_rate)
THEMECLR:     str        = 'rgb(0,206,209)'
TITLE:        str        = 'Awesome sound'
VERISONS:     tuple      = ('v.0.5', 'v.0.6')
HEIGHT:       int        = 473
WIDTH:        int        = 539

SHORTCUTS: dict = {
    'PLAY-PAUSE': 'Space',
    'PREV SONG': '-',
    'NEXT SONG': '+',
}
