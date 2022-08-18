import sys
import unittest
sys.path.append('.')
from comps.song import Song
from comps.musicplayer import (
    PlayerError,
    MusicPlayer,
)


class TestPlayer(unittest.TestCase):
    def setUp(self) -> None:
        self.player = MusicPlayer(Song(['1', '2']))

    def tearDown(self) -> None:
        self.player._is_playing = True
        self.player.set_volume(100)

    def test_set_volume(self):
        self.assertRaises(PlayerError, self.player.set_volume, 101)
        self.assertRaises(PlayerError, self.player.set_volume, -1)
        try:
            self.player.set_volume(0)
            self.player.set_volume(100)
            self.player.set_volume(30)
        except PlayerError as e:
            self.player.__class__.__name__
            self.fail(f"{self.player.__class__.__name__}.set_volume raised an unexpexted error: {e}")

    def test_play_pause(self):
        for _ in range(20):
            self.player.play()
            self.assertFalse(self.player)
            self.player.play()
            self.assertTrue(self.player)

    def test_set_timestamp(self): ... # TODO: Later
