import os
from logger import Logger
from jsonwrapper import Handler
from pathlib import Path
from typing import (
    Callable,
    Tuple,
    Dict,
    Any,
)


__all__ = (
    'SOURCE_CODE',
    'BASE_DIR',
    'PREVIOUS_BTN',
    'PAUSE_BTN',
    'SONGS_DIR',
    'PLAY_BTN',
    'NEXT_BTN',
    'MUTE_BTN',
    'RECORD_BTN',
    'BACKGROUND',
    'BACKWARD_ARR',
    'FORWARD_ARR',
    'LOGO',
    'PLAYERUI',
    'FPS',
    'LYRICS_DIR',
    'THEMECLR',
    'TITLE',
    'VERISONS',
    'VERISONS',
    'SHORTCUTS',
    'SUPPORTED_SONG_FORMATS',
    'SUPPORTED_LYRICS_FORMATS',
    'CONFIG',
    'logger',
    'config',
    'get_song_list',
)


def lyrics_dir(base_dir: Path) -> str:
    file = Path(base_dir, 'lyrics')
    if not os.path.exists(file):
        os.mkdir(file)
    return str(file)


def get_song_list(song_dir: str) -> Tuple[str, ...]:
    return tuple(filter(lambda i: i != '.gitignore', os.listdir(song_dir)))


FpsLike = Callable[[int], int]

SOURCE_CODE = 'https://github.com/hor00s/Awesome-sound'
BASE_DIR: Path = Path(__file__).parent.parent.parent
LOG_DIR = os.path.join(BASE_DIR, '.logs.txt')
SONGS_DIR: str = os.path.join(BASE_DIR, 'player', 'songs')
PREVIOUS_BTN: str = os.path.join('images', 'previous-button.png')
PAUSE_BTN: str = os.path.join('images', 'pause-button.png')
PLAY_BTN: str = os.path.join('images', 'play-button.png')
NEXT_BTN: str = os.path.join('images', 'next-button.png')
MUTE_BTN: str = os.path.join('images', 'mute-button.png')
RECORD_BTN: str = os.path.join('images', 'record.png')
BACKGROUND: str = os.path.join('images', 'background.png')
BACKWARD_ARR: str = os.path.join('images', 'backward-arr.png')
FORWARD_ARR: str = os.path.join('images', 'forward-arr.png')
LOGO: str = os.path.join('images', 'applogo.png')
PLAYERUI: str = os.path.join('window', 'player.ui')
CONFIG_FILE = os.path.join(BASE_DIR, '.config.json')
FPS: FpsLike = lambda frame_rate: int(1000 / frame_rate)
LYRICS_DIR: str = lyrics_dir(BASE_DIR)
THEMECLR: str = 'rgb(0,206,209)'
TITLE: str = 'Awesome sound'
DONWLOAD_DIR = Path(Path.home(), 'Downloads')
VERISONS: Tuple[str, ...] = (
    'v.0.5',
    'v.0.6',
    'v.0.7',
    'v.0.8',
    'v.0.9',
    'v.1.0',
)

SHORTCUTS: Dict[str, str] = {
    'PLAY-PAUSE': 'Space',
    'PREV SONG': '-',
    'NEXT SONG': '+',
    'DELETE SONG': 'del',
    'MUTE': 'm',
    'TRIM TRIGGER': 't',
}

CONFIG: Dict[Any, Any] = {
    'download_dir': str(DONWLOAD_DIR),
    'volume': 100,
    'is_muted': False,
    'last_song': {},
}

SUPPORTED_SONG_FORMATS: Tuple[str, ...] = (
    'mp3',
)

SUPPORTED_LYRICS_FORMATS: Tuple[str, ...] = (
    'srt',
)

# CONFIG EXAMPLE
#  {
#      "download_dir": "~/Downloads" (Configurable)
#      "volume": 59,
#      "is_muted": true,
#      "last_song": {
#          "song": "12 Stones - Anthem for the Underdog.mp3",
#          "timestamp": 8.11
#      },
#
#      -- DELAYS --
#      "songs/12 Stones - Anthem for the Underdog.mp3.delay": 1.0
#  }


logger = Logger(1, LOG_DIR)
config = Handler(CONFIG_FILE, CONFIG)
if not os.path.exists(CONFIG_FILE):
    config.init()
