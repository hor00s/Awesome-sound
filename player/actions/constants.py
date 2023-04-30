import os
from pathlib import Path
from typing import Callable


def lyrics_dir(base_dir: Path):
    file = Path(base_dir, 'lyrics')
    if not os.path.exists(file):
        os.mkdir(file)
    return str(file)


FpsLike = Callable[[int], int]


BASE_DIR:     Path       = Path(__file__).parent.parent.parent
SONGSFILE:    tuple[str] = tuple(filter(lambda i: i != '.gitignore', os.listdir('songs')))
PREVIOUS_BTN: str        = os.path.join('images', 'previous-button.png')
PAUSE_BTN:    str        = os.path.join('images', 'pause-button.png')
PLAY_BTN:     str        = os.path.join('images', 'play-button.png')
NEXT_BTN:     str        = os.path.join('images', 'next-button.png')
BACKGROUND:   str        = os.path.join('images', 'background.png')
LOGO:         str        = os.path.join('images', 'applogo.png')
PLAYERUI:     str        = os.path.join('window', 'player.ui')
FPS:          FpsLike    = lambda frame_rate: int(1000 / frame_rate)
LYRICS_DIR:   str        = lyrics_dir(BASE_DIR)
THEMECLR:     str        = 'rgb(0,206,209)'
TITLE:        str        = 'Awesome sound'
HEIGHT:       int        = 473
WIDTH:        int        = 539
VERISONS:     tuple      = (
    'v.0.5',
    'v.0.6',
    'v.0.7',
)

SHORTCUTS: dict = {
    'PLAY-PAUSE': 'Space',
    'PREV SONG': '-',
    'NEXT SONG': '+',
}
