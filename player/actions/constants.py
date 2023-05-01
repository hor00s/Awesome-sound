import os
from pathlib import Path
from typing import (
    Callable,
    Tuple,
    Dict,
)


__all__ = (
    'BASE_DIR',
    'SONGSLIST',
    'PREVIOUS_BTN',
    'PAUSE_BTN',
    'PLAY_BTN',
    'NEXT_BTN',
    'BACKGROUND',
    'LOGO',
    'PLAYERUI',
    'FPS',
    'LYRICS_DIR',
    'THEMECLR',
    'TITLE',
    'VERISONS',
    'VERISONS',
    'SHORTCUTS',
)


def lyrics_dir(base_dir: Path) -> str:
    file = Path(base_dir, 'lyrics')
    if not os.path.exists(file):
        os.mkdir(file)
    return str(file)


FpsLike = Callable[[int], int]


BASE_DIR: Path = Path(__file__).parent.parent.parent
SONGSLIST: Tuple[str, ...] = tuple(filter(lambda i: i != '.gitignore', os.listdir('songs')))
PREVIOUS_BTN: str = os.path.join('images', 'previous-button.png')
PAUSE_BTN: str = os.path.join('images', 'pause-button.png')
PLAY_BTN: str = os.path.join('images', 'play-button.png')
NEXT_BTN: str = os.path.join('images', 'next-button.png')
BACKGROUND: str = os.path.join('images', 'background.png')
LOGO: str = os.path.join('images', 'applogo.png')
PLAYERUI: str = os.path.join('window', 'player.ui')
FPS: FpsLike = lambda frame_rate: int(1000 / frame_rate)
LYRICS_DIR: str = lyrics_dir(BASE_DIR)
THEMECLR: str = 'rgb(0,206,209)'
TITLE: str = 'Awesome sound'
VERISONS: Tuple[str, ...] = (
    'v.0.5',
    'v.0.6',
    'v.0.7',
)

SHORTCUTS: Dict[str, str] = {
    'PLAY-PAUSE': 'Space',
    'PREV SONG': '-',
    'NEXT SONG': '+',
}
