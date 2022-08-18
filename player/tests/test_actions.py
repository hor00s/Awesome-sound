import sys
import unittest
sys.path.append('.')
from comps.musicplayer import MusicPlayer
from comps.musicplayer import Song
from actions.actions import (
    play_btn_switcher,
    clear_song_extension,
)
from actions.constants import (
    PLAY_BTN,
    PAUSE_BTN,
)

class TestActions(unittest.TestCase):
    def setUp(self) -> None:
        self.player = MusicPlayer(Song(['song1', 'song2', '...']))

    def test_switcer(self):
        for _ in range(20):
            self.assertTrue(self.player)
            self.assertEqual(play_btn_switcher(self.player, 'btn', 'pyglet', testing=True), PLAY_BTN)
            self.assertFalse(self.player)
            self.assertEqual(play_btn_switcher(self.player, 'btn', 'pyglet', testing=True), PAUSE_BTN)
            self.assertTrue(self.player)

    def test_clear_extension(self):
        s0 = 'test.mp3'
        self.assertEqual(clear_song_extension(s0), 'test')
        s1 = 'test.FLAC'
        self.assertEqual(clear_song_extension(s1), 'test')
        s2 = 'Austronaut in the ocean.mp3'
        self.assertEqual(clear_song_extension(s2), 'Austronaut in the ocean')
        s3 = 'Austronaut.in.the ocean.mp3'
        self.assertEqual(clear_song_extension(s3), 'Austronaut.in.the ocean')
        s4 = 'Austronaut.in.the ocean.FLAC'
        self.assertEqual(clear_song_extension(s4), 'Austronaut.in.the ocean')
        s5 = 'Austronaut.in. the ocean.FLAC'
        self.assertEqual(clear_song_extension(s5), 'Austronaut.in. the ocean')
