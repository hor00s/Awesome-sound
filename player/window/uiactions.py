import os
import shutil
import traceback
import datetime
from pytube import YouTube
from jsonwrapper import Handler
from lyricshandler import Creator
from .languages import get_message
from typing import (
    List,
    Tuple,
    Union,
    Iterable,
)
from comps import (
    Disk,
    MusicPlayer
)
from actions import (
    logger,
    get_active_language,
)


def get_delay_key(disk: Disk) -> str:
    """
    :param disk: The current disk object
    :type disk: Disk
    :return: It's full path with `.delay` extension (`songs/<song_name>.mp3.delay`)
    :rtype: str
    """
    return f"{disk.song_path}.delay"


def log_error(err: Exception) -> None:
    """If an error occures, modify it into a proper format
    and write it in app's logs

    :param err: The error object that occured
    :type err: Exception
    """
    long_error = traceback.format_exc()
    err_format = f"""{get_datetime()}
Short description: {err}
Detailed description: {long_error}"""
    logger.error(err_format)


def filter_song_name(song_name: str, forbidden_chars: Iterable[str]) -> str:
    return ''.join(char for char in song_name if char not in forbidden_chars)


def get_datetime() -> datetime.datetime:
    """A quick way to get system's datetime

    :return: Example `2023-05-06 13:43:28.200578`
    :rtype: datetime.datetime
    """
    return datetime.datetime.now()


def get_disk(config: Handler, song_list: Tuple[str, ...]) -> Disk:
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
        return Disk(song_list, last_song['song'])
    return Disk(song_list)


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
    sound_to_srt = player.disk.song_name + extension
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
    lang = get_active_language()
    dt = get_datetime()
    try:
        delay = float(delay)
        if key in config:
            prev_delay = config.get(key)
            config.edit(key, delay)
            msg = f"{dt} {get_message(lang, 'delay_changed', key, prev_delay, '->', delay)}"
            logger.debug(msg)
        else:
            config.add(key, delay)
            msg = f"{dt} {get_message(lang, 'delay_set', key, '->', delay)}"
            logger.debug(msg)
    except ValueError:
        msg = f"{dt} {get_message(lang, 'delay_invalid', delay)}"
        logger.warning(msg)
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
    dt = get_datetime()
    lang = get_active_language()
    creator = Creator(player, lyrics_dir)
    lyrics_location = creator.manual_save(path)
    logger.debug(f"{dt} {get_message(lang, 'import_lyrics'), path}")
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
        if song != os.path.join(target_dir, song):
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


def export_song(path: str, song_mp3: str, target_dir: str) -> None:
    src = os.path.join(path, song_mp3)
    if src != os.path.join(target_dir, song_mp3):
        shutil.copy(src, target_dir)
        # TODO: Test


def even_spaces(first_word: str, space_buffer: int) -> str:
    """Give a fixed ammount of spaces of a given word. Example
        ```
            >>> space_buffer = 10
            >>>
            >>> first, second = 'word' 'something'
            >>> spaces = even_spaces(first, space_buffer)
            >>> msg1 = f"{first}{spaces}{secons}"
            >>>
            >>> first, second = 'or', 'text'
            >>> spaces = even_spaces(first, space_buffer)
            >>> msg2 = f"{first}{spaces}{secons}"
            >>> msg1
            'word      something'
            >>> msg2
            'or        text'
            >>> f"{msg1}\\n{msg2}"
            >>> 'word      something'
            >>> 'or        text'
        ```

    :param first_word: The first word tha the spaces will be determined from
    :type first_word: str
    :param space_buffer: The fixed ammount of spaces needed
    :type space_buffer: int
    :return: The `first_word` with the according ammont of space `' '` chars
    :rtype: str
    """
    spaces = space_buffer - len(first_word)
    return " " * spaces


def rename(path: str, file_name: str, new_name: str,
           extension: str, forbidden_chars: Iterable[str]) -> None:
    """This function can rename a song preserving its position and extension automatically

    :param path: Source path to the song that is to be renamed
    :type path: str
    :param file_name: The file where the source song is located
    :type file_name: str
    :param new_name: The name the song will be changed to (suggesting without extension)
    :type new_name: str
    :param extension: The extension to be inserted automatically to the new name
    :type extension: str
    """
    src = os.path.join(path, file_name + extension)
    dst = os.path.join(path, f"{filter_song_name(new_name, forbidden_chars)}{extension}")
    print(dst)
    os.rename(src, dst)


def search_song(songs: Tuple[str, ...], query: str, default_index: int) -> int:
    """Find the first match in a list from the query

    :param songs: A list of potentional matches
    :type songs: Tuple[str, ...]
    :param query: A text that the search will be based on
    :type query: str
    :param default_index: A default index that will be returned if no matches are found
    :type default_index: int
    :raises IndexError: In case the `default_index` is >= len(songs)
    :return: The first match of the query or `default_index` if no matches are found
    :rtype: int
    """
    if default_index >= len(songs):
        raise IndexError(f"default_index `{default_index}` is greater than songs `{len(songs)}`")
    for index, song in enumerate(songs):
        if query.lower() in song.lower():
            return index
    return default_index


def time_to_total_seconds(time: str) -> float:
    time_obj = datetime.datetime.strptime(time, '%H:%M:%S')
    total_seconds = datetime.timedelta(hours=time_obj.hour, minutes=time_obj.minute,
                                       seconds=time_obj.second).seconds
    return total_seconds


def download_audio(yt_link: str, dst_path: str, forbidden_chars: Iterable[str]) -> None:
    video = YouTube(yt_link)
    video = video.streams.get_audio_only()  # type: ignore

    path = video.download(dst_path)

    audio_name = path.split(os.sep)[-1]
    audio_name = path.split(os.sep)[-1][:audio_name.rfind('.')] + '.mp3'

    os.rename(path, os.path.join(dst_path, filter_song_name(audio_name, forbidden_chars)))
