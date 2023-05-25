import os
import sys
from logger import Logger
from jsonwrapper import Handler
from pathlib import Path
from typing import (
    Literal,
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
    'LYRICS_ICON',
    'LOGO',
    'PLAYERUI',
    'LYRICS_DIR',
    'ACTIONS_DIR',
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
    'Language',
    'get_active_language',
    'get_actions_dir',
)


Language = Literal[
    'en',
    'gr',
]


def get_active_language() -> Language:
    language: Language = config['language']
    return language


def lyrics_dir(base_dir: Path) -> str:
    file = Path(base_dir, 'lyrics')
    if not os.path.exists(file):
        os.mkdir(file)
    return str(file)


def get_actions_dir(base_dir: Path) -> str:
    file = Path(base_dir, '.actions')
    if not os.path.exists(file):
        os.mkdir(file)
    return str(file)


def get_song_list(song_dir: str) -> Tuple[str, ...]:
    return tuple(sorted(filter(lambda i: i != '.gitignore', os.listdir(song_dir))))


def get_songs_dir(base_dir: Path) -> str:
    path = os.path.join(base_dir, 'player', 'songs')
    if not os.path.exists(path):
        os.mkdir(path)
    return path


SOURCE_CODE = 'https://github.com/hor00s/Awesome-sound'
BASE_DIR: Path = Path(__file__).parent.parent.parent
LOG_DIR = os.path.join(BASE_DIR, '.logs.txt')
SONGS_DIR: str = get_songs_dir(BASE_DIR)
PREVIOUS_BTN: str = os.path.join(BASE_DIR, 'player', 'images', 'previous-button.png')
PAUSE_BTN: str = os.path.join(BASE_DIR, 'player', 'images', 'pause-button.png')
PLAY_BTN: str = os.path.join(BASE_DIR, 'player', 'images', 'play-button.png')
NEXT_BTN: str = os.path.join(BASE_DIR, 'player', 'images', 'next-button.png')
MUTE_BTN: str = os.path.join(BASE_DIR, 'player', 'images', 'mute-button.png')
RECORD_BTN: str = os.path.join(BASE_DIR, 'player', 'images', 'record.png')
BACKGROUND: str = os.path.join(BASE_DIR, 'player', 'images', 'background.png')
BACKWARD_ARR: str = os.path.join(BASE_DIR, 'player', 'images', 'backward-arr.png')
FORWARD_ARR: str = os.path.join(BASE_DIR, 'player', 'images', 'forward-arr.png')
LYRICS_ICON: str = os.path.join(BASE_DIR, 'player', 'images', 'song-lyrics.png')
LOGO: str = os.path.join(BASE_DIR, 'player', 'images', 'applogo.png')
PLAYERUI: str = os.path.join(BASE_DIR, 'player', 'window', 'player.ui')
CONFIG_FILE = os.path.join(BASE_DIR, '.config.json')
ACTIONS_DIR: str = get_actions_dir(BASE_DIR)
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
    'v.1.1',
    'v.1.2',
    'v.1.3',
    'v.1.4',
    'v.1.5',
    'v.1.6',
    'v.1.7',
)

SHORTCUTS: Dict[str, str] = {
    'PLAY-PAUSE': 'Space',
    'PREV SONG': '-',
    'NEXT SONG': '+',
    'DELETE SONG': 'del',
    'MUTE': 'm',
    'TRIM TRIGGER': 't',
    'LYRICS TRIGGER': 'l',
    'MAIN WINDOW FOCUS': 'esc',
    'SELECT SONG': 'Enter',
}

CONFIG: Dict[Any, Any] = {
    'language': 'en',
    'max_frame_rate': 20,
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
#      "language": 'en'
#      "max_frame_rate": 20,
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


if 'unittest' in sys.modules.keys():
    # If program runs with unittest, set logger level to `level 5`
    # so it doesn't log anything in stdout and in file
    logger.settings.level = 5
