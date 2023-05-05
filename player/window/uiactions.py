import os
import shutil
import traceback
import datetime
from lyricshandler import Creator
from jsonwrapper import Handler
from typing import (
    List,
    Union,
    Iterable,
)
from comps import (
    Disk,
    MusicPlayer
)
from actions import (
    SONGS_DIR,
    logger,
    get_song_list,
)


def log_error(err: Exception) -> None:
    long_error = traceback.format_exc().replace('\n', ' ')
    err_format = f"""{get_datetime()} Short description: {err}\
 Detailed description: {long_error}""".strip()
    logger.error(err_format)


def write_error(error: Exception, path: str) -> None:
    date_time = datetime.datetime.now()
    with open(path, mode='a') as f:
        error_format = f"""
---------------------------
{date_time}
Short error: {error}
Detailed: {traceback.format_exc()}
---------------------------
        """
        f.write(error_format)


def get_datetime() -> datetime.datetime:
    return datetime.datetime.now()


def get_disk(config: Handler) -> Disk:
    last_song = config.get('last_song')
    if last_song:
        return Disk(get_song_list(SONGS_DIR), last_song['song'])
    return Disk(get_song_list(SONGS_DIR))


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
        delay = float(delay)
        if key in config:
            prev_delay = config.get(key)
            config.edit(key, delay)
            msg = f"{get_datetime()} Delay was changed for {key} from `{prev_delay}` -> `{delay}`"
            logger.debug(msg)
        else:
            config.add(key, delay)
            msg = f"{get_datetime()} Delay has been set for {key} to `{delay}` seconds"
            logger.debug(msg)
    except ValueError:
        logger.warning(f"{get_datetime()} {delay} is not allowed\
 as value for lyrics delay. Please choose a numeric one")
        # User passed non numeric value


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
    logger.debug(f"{get_datetime()} Lyrics file moved from {path} -> {lyrics_location}")
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


def import_songs(songs: List[str], target_dir: str) -> None:
    for song in songs:
        shutil.copy(song, target_dir)
