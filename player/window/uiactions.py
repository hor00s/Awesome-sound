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
    """If an error occures, modify it into a proper format
    and write it in app's logs

    :param err: The error object that occured
    :type err: Exception
    """
    long_error = traceback.format_exc().replace('\n', ' ')
    err_format = f"""{get_datetime()} Short description: {err}\
 Detailed description: {long_error}""".strip()
    logger.error(err_format)


def get_datetime() -> datetime.datetime:
    """A quick way to get system's datetime

    :return: Example `2023-05-06 13:43:28.200578`
    :rtype: datetime.datetime
    """
    return datetime.datetime.now()


def get_disk(config: Handler) -> Disk:
    """Check if a `last_song` exists in app's config and construct
    a new `Disk` object with a refreshed song list and `last_song`
    if it exists, default song otherwise

    :param config: The app's config handler
    :type config: Handler
    :return: The new `Disk` object
    :rtype: Disk
    """
    last_song = config.get('last_song')
    if last_song:
        return Disk(get_song_list(SONGS_DIR), last_song['song'])
    return Disk(get_song_list(SONGS_DIR))


def get_lyrics_file(lyrics_dir: str, player: MusicPlayer, extension: str) -> str:
    """This function looks if a given song has an according lyrics file in `lyrics_dir`

    :param lyrics_dir: The directory where lyrics are saved
    :type lyrics_dir: str
    :param player: The main `MusicPlayer` object
    :type player: MusicPlayer
    :param extension: The standard lyrics extension
    :type extension: str
    :return: The lyrics file path of a given song if exists. Otherwise,
    construct a fake one and return its path
    :rtype: str
    """
    sound_to_srt = player.disk.title() + extension
    lyrics_file = os.path.join(lyrics_dir, sound_to_srt)
    if not os.path.exists(lyrics_file):
        lyrics_file = os.path.join(lyrics_dir, 'fake.srt')
        with open(lyrics_file, mode='w') as f:
            f.write("1\n00:00:00,000 --> 00:25:00,000\n")
    return lyrics_file


def set_lyrics_delay(key: str, delay: Union[str, float], config: Handler) -> None:
    """Edit an existing lyrics delay setup for the current playing song if it exists.
    Add a delay configuration for a given song if it doens't exist

    :param key: The key that the delay is assigned as (`song/<song>.mp3.delay)
    :type key: str
    :param delay: The delay `x` number of seconds.
    :type delay: Union[str, float]
    :param config: The app's main config Handler
    :type config: Handler
    """
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
    """Reverse the `player`'s mute state and edit the config accordingly

    :param player: The main `MusicPlayer` object
    :type player: MusicPlayer
    :param config: The app's config Handler
    :type config: Handler
    """
    if player.is_muted:
        player.unmute()
        config.edit('is_muted', False)
    else:
        player.mute()
        config.edit('is_muted', True)


def manual_save_lyrics(path: str, player: MusicPlayer, lyrics_dir: str) -> str:
    """Manualy set a pre-downloaded lyrics file for the current playing song and
    change its name to match its in-app name

    :param path: The external path of the downlowded lyrics file
    :type path: str
    :param player: The main app's player object
    :type player: MusicPlayer
    :param lyrics_dir: The standard app's lyrics directory
    :type lyrics_dir: str
    :return: The path to the lyric's file in the app's lyrics dir
    :rtype: str
    """
    creator = Creator(player.disk, lyrics_dir)
    lyrics_location = creator.manual_save(path)
    logger.debug(f"{get_datetime()} Lyrics file moved from {path} -> {lyrics_location}")
    return lyrics_location


def make_file_types(file_types: Iterable[str]) -> str:
    """Contruct a string of the file types to be used in the
    file explorer

    :param file_types: An iterable of allowed extension
    Example ('mp3', 'mp4', ...)
    :type file_types: Iterable[str]
    :return: A string that matches Qt's filedialog syntax
        ```
        >>> # Example
        >>> types = ('mp3', 'mp4')
        >>> make_file_types(types)
        'Mp3 files (*.mp3);;Mp4 Files (*.mp4)'
        ```
    :rtype: str
    """
    types = ""
    for type_ in file_types:
        name = f"{type_.title()} files"
        ext = f"(*.{type_})"
        field = f"{name} {ext};;"
        types += field
    return types


def edit_volume(config: Handler, player: MusicPlayer, volume: int) -> None:
    """Edit the app's `volume` config to `volume` parameter and set main player
    object to that if the `player` is not muted. Otherwise, edit config
    and let the `player`'s volume untouched

    :param config: The main app's config Handler
    :type config: Handler
    :param player: The main app's player object
    :type player: MusicPlayer
    :param volume: The new volume to be set
    :type volume: int
    """
    config.edit('volume', int(volume))
    if not player.is_muted:
        player.set_volume(config.get('volume'))


def import_songs(songs: List[str], target_dir: str) -> None:
    """Move a list of songs to app's main song directory

    :param songs: A list of full paths of songs to be imported
    :type songs: List[str]
    :param target_dir: The main app's songs directory
    :type target_dir: str
    """
    for song in songs:
        shutil.copy(song, target_dir)
        logger.debug(f"{song} -> {target_dir}")


def delete_song(path: str, song_name: str) -> None:
    """Delete a song from main app's directory

    :param path: The path to app's songs directory
    :type path: str
    :param song_name: The name of the song to be delete with it's extension
        ```
        >>> # Example
        >>> path, song_name = '<path_to_app's_songs_dir>, <song_name>.mp3'
        >>> delete_song(path, song_name)  # <path_to_app's_songs_dir>/<song_name>.mp3 gets deleted
        None
        ```
    :type song_name: str
    """
    song_path = os.path.join(path, song_name)
    os.remove(song_path)
    logger.warning(f"Song {song_name} has been deleted")
