import os
from lyricshandler import Creator
from jsonwrapper import Handler

from typing import (
    Union,
    Iterable,
)
from comps import (
    Disk,
    MusicPlayer
)
from actions import (
    SONGSLIST,
)


def get_disk(config: Handler) -> Disk:
    last_song = config.get('last_song')
    if last_song:
        return Disk(SONGSLIST, last_song['song'])
    return Disk(SONGSLIST)


def get_lyrics_file(lyrics_dir: str, player: MusicPlayer, extension: str) -> str:
    sound_to_srt = player.disk.title() + extension
    lyrics_file = os.path.join(lyrics_dir, sound_to_srt)
    if not os.path.exists(lyrics_file):
        lyrics_file = os.path.join(lyrics_dir, 'fake.srt')
        with open(lyrics_file, mode='w') as f:
            f.write("1\n00:00:00,000 --> 00:25:00,000\n")
    return lyrics_file


def set_lyrics_delay(key: str, delay: Union[str, float], config: Handler) -> None:
    try:
        if key in config:
            config.edit(key, float(delay))
        else:
            config.add(key, float(delay))
    except ValueError:
        # User passed non numeric value
        pass


def mute_setup(player: MusicPlayer, config: Handler) -> None:
    if player.is_muted:
        player.unmute()
        config.edit('is_muted', False)
    else:
        player.mute()
        config.edit('is_muted', True)


def manual_save_lyrics(path: str, player: MusicPlayer, lyrics_dir: str) -> str:
    creator = Creator(player.disk, lyrics_dir)
    lyrics_location = creator.manual_save(path)
    return lyrics_location


def make_file_types(file_types: Iterable[str]) -> str:
    types = ""
    for type_ in file_types:
        name = f"{type_.title()} files"
        ext = f"(*.{type_})"
        field = f"{name} {ext};;"
        types += field
    return types


def edit_volume(config: Handler, player: MusicPlayer, volume: int) -> None:
    config.edit('volume', int(volume))
    if not player.is_muted:
        player.set_volume(config.get('volume'))
