import sys
import unittest
sys.path.append('.')
from comps.musicplayer import Song


class TestPlayer(unittest.TestCase):
    def setUp(self) -> None:
        other_list = ['1', '2', '4']
        self.songs = ['Astronaut', 'Tones And I', 'Lose yourself', 'Sing for the momment', 'Audacity']
        self.song = Song(self.songs)
        self.song2 = Song(other_list)

    def tearDown(self) -> None:
        self.song._playing_index = 0

    def test_singletone(self):
        self.assertIs(self.song, self.song2)

    def test_current_song(self):
        self.assertEqual(self.song.current_song, self.songs[0])

    def test_next(self):
        self.assertEqual(self.song.next(), self.songs[1])
        self.assertEqual(self.song.next(), self.songs[2])

        self.assertEqual(self.song2.current_song, self.song.current_song)

    def test_prev(self):
        self.song._playing_index = 2
        self.assertEqual(self.song.prev(), self.songs[1])
        self.assertEqual(self.song.prev(), self.songs[0])

        self.assertEqual(self.song2.current_song, self.song.current_song)

    def test_song_index_up(self):
        self.song._playing_index = len(self.songs) - 1
        self.assertEqual(self.song.next(), self.songs[0])

    def test_song_index_down(self):
        self.song._playing_index = 0
        self.assertEqual(self.song.prev(), self.songs[-1])
        self.assertEqual(self.song._playing_index, len(self.songs)-1)

    def test_user_pick(self):
        self.assertEqual(self.song.user_pick(2), self.songs[2])
        self.assertEqual(self.song._playing_index, 2)
        self.assertRaises(IndexError, self.song.user_pick, -2)
