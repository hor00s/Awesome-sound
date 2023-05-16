import unittest
import os
import shutil
from comps import (
    MusicPlayer,
    Disk,
)
from jsonwrapper import Handler
from actions import (
    BASE_DIR,
    CONFIG,
    SONGS_DIR,
    get_song_list,
)
from .uiactions import (
    get_delay_key,
    get_disk,
    get_lyrics_file,
    set_lyrics_delay,
    mute_setup,
    manual_save_lyrics,
    make_file_types,
    edit_volume,
    import_songs,
    delete_song,
    even_spaces,
    export_song,
    rename,
    search_song,
)

BASE_TEST_DIR = os.path.join(BASE_DIR, 'player', 'window' '.ui_test_dir')
if os.path.exists(BASE_TEST_DIR):
    shutil.rmtree(BASE_TEST_DIR)
os.mkdir(BASE_TEST_DIR)

test_lyrics_dir = os.path.join(BASE_TEST_DIR, '.test_lyrics_dir')
test_songs_dir = os.path.join(BASE_TEST_DIR, '.test_songs_dir')
test_lyrics_file = os.path.join(BASE_TEST_DIR, '.test_lyrics.srt')

if not os.path.exists(test_songs_dir):
    os.mkdir(test_songs_dir)
if not os.path.exists(test_lyrics_dir):
    os.mkdir(test_lyrics_dir)
if not os.path.exists(test_lyrics_file):
    with open(test_lyrics_file, mode='w') as _:
        ...

test_config_file = os.path.join(BASE_TEST_DIR, '.test_config.json')
EXTENSION = 'srt'

TEST_CONFIG = {
    'donwload_dir': '',
    'volume': 100,
    'is_muted': False,
    'last_song': {},
}

test_config = Handler(test_config_file, TEST_CONFIG)


SONGS: tuple[str, ...] = (
    'Gustavo Santaolalla - Babel (Trap Remix).mp3',
    'Motto-trimmed.mp3',
    'The Neighbourhood - Sweater Weather (Ozgur Arslan Remix).mp3',
    'tiesto go down deh.mp3',
    'Tion Wayne - IFTK (Feat. La Roux).mp3',
    'Tion Wayne - IFTK (Feat. La Roux)-Ringtone-trimmed.mp3',
    'Want Ya.mp3',
)


class TestUiActions(unittest.TestCase):
    def setUp(self) -> None:
        test_config.init()
        self.disk = Disk(SONGS)
        self.player = MusicPlayer(self.disk, test_config.get('is_muted', False),
                                  test_config.get('volume', False))
        return super().setUp()

    def tearDown(self) -> None:
        test_config.purge()
        return super().tearDown()

    def test_get_disk(self) -> None:
        # Test with default song
        index = 0
        songs = SONGS
        disk = get_disk(test_config, songs)
        self.assertEqual(disk.song_mp3, songs[index])
        self.assertEqual(disk.song_index, index)

        # Test with set song
        index = 3
        songs = SONGS
        CONFIG['last_song'] = {'song': songs[index], 'timestamp': 1.1}
        os.remove(test_config._file)
        test_config._config = CONFIG
        test_config.init()
        disk = get_disk(test_config, songs)
        songs = SONGS
        self.assertEqual(disk.song_mp3, songs[index])
        self.assertEqual(disk.song_index, index)

    def test_get_lyrics_file(self) -> None:
        test_config.init()
        lyrics_dir = get_lyrics_file(test_lyrics_dir, self.player, EXTENSION)
        self.assertTrue(os.path.exists(lyrics_dir))

    def test_set_lyrics_delay(self) -> None:
        delay = 1
        key = get_delay_key(self.player.disk)

        set_lyrics_delay(key, delay, test_config)
        self.assertEqual(test_config.get(key), delay)
        self.assertIsInstance(test_config.get(key), float)
        # Just make sure this doesn't raise an exception
        set_lyrics_delay(key, 'non-numeric', test_config)

    def test_mute_setup(self) -> None:
        mute_state = self.player.is_muted
        mute_setup(self.player, test_config)
        self.assertIs(not mute_state, self.player.is_muted)
        self.assertIs(not mute_state, test_config.get('is_muted'))

        mute_state = self.player.is_muted
        mute_setup(self.player, test_config)
        self.assertIs(not mute_state, self.player.is_muted)
        self.assertIs(not mute_state, test_config.get('is_muted'))

    def test_manual_save_lyrics(self) -> None:
        lyrics_loc = manual_save_lyrics(test_lyrics_file, self.player, test_lyrics_dir)
        self.assertTrue(os.path.exists(lyrics_loc))
        os.remove(lyrics_loc)

    def test_make_file_types(self) -> None:
        types = make_file_types(('srt', 'py'))
        expected = "Srt files (*.srt);;Py files (*.py);;"
        self.assertEqual(types, expected)

    def test_edit_volume(self) -> None:
        vol = 10
        edit_volume(test_config, self.player, vol)
        config_volume = test_config.get('volume')
        player_volume = self.player.volume
        self.assertEqual(vol, config_volume)
        self.assertEqual(vol, player_volume)

        # MUTE PLAYER
        # Since player is muted, `edit_volume` should not touch `player.volume` untill its unmuted
        self.player.mute()
        vol2 = 20
        edit_volume(test_config, self.player, vol2)
        config_volume = test_config.get('volume')
        self.assertEqual(config_volume, vol2)
        self.assertNotEqual(self.player.volume, vol2)
        self.assertEqual(self.player.volume, vol)

    def _test_import_songs(self) -> None:
        songs = list(get_song_list(SONGS_DIR))
        path_list = list(map(lambda song: os.path.join(SONGS_DIR, song), songs))

        import_songs(path_list, test_songs_dir)
        result = sorted(os.listdir(test_songs_dir))

        self.assertEqual(songs, result)

    def test_delete_song(self) -> None:
        # TODO: Find a way to test this without deleteing
        # a song from the main directory
        delete_song

    def test_even_spaces(self) -> None:
        first_word, second_word = 'test', 'other'
        spaced = even_spaces(first_word, 7)
        expected = f"{first_word}   {second_word}"

        output = f"{first_word}{spaced}{second_word}"
        self.assertEqual(output, expected)

    def _test_export_song(self) -> None:
        """Copy a song from the local file system to
        a user defined directory anywhere outside
        """
        song = os.listdir(SONGS_DIR)[0]
        export_song(SONGS_DIR, song, '.')
        new_path = os.path.join('.', song)
        # self.assertTrue(os.path.exists(new_path))
        os.remove(new_path)

    def test_rename(self) -> None:
        rename
        _ = 'test'
        _ = '.mp3'
        # TODO: Test this without moving outside test_dir

    def test_search_songs(self) -> None:
        songs = (
            'a',
            'a',
            'b',
            'b',
            'c',
            'c',
            'd',
            'd',
            'e',
            'e',
            'f',
            'f',
        )

        default = 0
        result = search_song(songs, 'b', default)
        expected = 2
        self.assertEqual(result, expected)

        default = 3
        result = search_song(songs, '...', default)
        self.assertEqual(result, default)

        with self.assertRaises(IndexError):
            default = len(songs)
            result = search_song(songs, '...', default)
