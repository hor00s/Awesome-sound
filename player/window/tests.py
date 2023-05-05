import unittest
import os
from comps import (
    MusicPlayer,
    Disk,
)
from jsonwrapper import Handler
from actions import (
    BASE_DIR,
    CONFIG,
    SONGSLIST,
)
from .uiactions import (
    get_disk,
    get_lyrics_file,
    set_lyrics_delay,
    mute_setup,
    manual_save_lyrics,
    make_file_types,
    edit_volume,
)


test_lyrics_dir = os.path.join(BASE_DIR, 'player', 'window', '.test_lyrics_dir')
if not os.path.exists(test_lyrics_dir):
    os.mkdir(test_lyrics_dir)
test_config_file = os.path.join(BASE_DIR, 'player', 'window', '.test_config.json')
test_lyrics_file = os.path.join(BASE_DIR, '.test_lyrics.srt')
EXTENSION = 'srt'

TEST_CONFIG = {
    'volume': 100,
    'is_muted': False,
    'last_song': {},
}
test_config = Handler(test_config_file, TEST_CONFIG)


assert tuple(TEST_CONFIG.values()) == tuple(CONFIG.values())\
    and tuple(TEST_CONFIG.keys()) == tuple(CONFIG.keys()),\
    "There are inconsistencies between CONFIG and TEST_CONFIG"


class TestUiActions(unittest.TestCase):
    def setUp(self) -> None:
        test_config.init()
        self.disk = Disk(SONGSLIST)
        self.player = MusicPlayer(self.disk, test_config.get('is_muted', False),
                                  test_config.get('volume', False))
        return super().setUp()

    def tearDown(self) -> None:
        test_config.purge()
        return super().tearDown()

    def test_get_disk(self) -> None:
        # Test with default song
        index = 0
        disk = get_disk(test_config)
        self.assertEqual(disk.song_mp3, SONGSLIST[index])
        self.assertEqual(disk.song_index, index)

        # Test with set song
        index = 3
        CONFIG['last_song'] = {'song': SONGSLIST[index], 'timestamp': 1.1}
        os.remove(test_config._file)
        test_config._config = CONFIG
        test_config.init()
        disk = get_disk(test_config)
        self.assertEqual(disk.song_mp3, SONGSLIST[index])
        self.assertEqual(disk.song_index, index)

    def test_get_lyrics_file(self) -> None:
        test_config.init()
        lyrics_dir = get_lyrics_file(test_lyrics_dir, self.player, EXTENSION)
        self.assertTrue(os.path.exists(lyrics_dir))

    def test_set_lyrics_delay(self) -> None:
        delay = 1
        key = f"{self.disk.song_mp3}.delay"

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