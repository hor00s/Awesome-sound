import unittest
from comps import (
    MusicPlayer,
    Disk,
)
from actions import (
    PAUSE_BTN,
    PLAY_BTN,
    play_btn_switcher,
    clear_file_extension,
)


class TestActions(unittest.TestCase):
    def setUp(self) -> None:
        self.player = MusicPlayer(Disk(['song1', 'song2', '...']))

    def test_switcer(self):
        for _ in range(20):
            self.assertTrue(self.player)
            self.assertEqual(play_btn_switcher(self.player, 'btn',
                             'pyglet', testing=True), PLAY_BTN)
            self.assertFalse(self.player)
            self.assertEqual(play_btn_switcher(self.player, 'btn',
                             'pyglet', testing=True), PAUSE_BTN)
            self.assertTrue(self.player)

    def test_clear_extension(self):
        s0 = 'test.mp3'
        self.assertEqual(clear_file_extension(s0), 'test')
        s1 = 'test.FLAC'
        self.assertEqual(clear_file_extension(s1), 'test')
        s2 = 'Austronaut in the ocean.mp3'
        self.assertEqual(clear_file_extension(s2), 'Austronaut in the ocean')
        s3 = 'Austronaut.in.the ocean.mp3'
        self.assertEqual(clear_file_extension(s3), 'Austronaut.in.the ocean')
        s4 = 'Austronaut.in.the ocean.FLAC'
        self.assertEqual(clear_file_extension(s4), 'Austronaut.in.the ocean')
        s5 = 'Austronaut.in. the ocean.FLAC'
        self.assertEqual(clear_file_extension(s5), 'Austronaut.in. the ocean')
