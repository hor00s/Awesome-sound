import unittest
from comps import (
    Disk,
    PlayerError,
    MusicPlayer,
)


class TestPlayer(unittest.TestCase):
    def setUp(self) -> None:
        self.player = MusicPlayer(Disk(['1', '2']))

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
            err = f"{self.player.__class__.__name__}.set_volume raised an unexpexted error: {e}"
            self.fail(err)

    def test_play_pause(self):
        for _ in range(20):
            self.player.playing()
            self.assertFalse(self.player)
            self.player.playing()
            self.assertTrue(self.player)

    def test_set_timestamp(self): ...  # TODO: Later
