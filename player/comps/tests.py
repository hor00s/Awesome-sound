import unittest
import os
from .disk import Disk
from .musicplayer import (
    MusicPlayer,
    PlayerError,
)


SONGS = (
    "practical.mp3",
    "disk.mp3",
    "fashion.mp3",
    "chief.mp3",
    "as.mp3",
    "anticipation.mp3",
    "remedy.mp3",
    "tasty.mp3",
    "stand.mp3",
    "stuff.mp3",
    "scream.mp3",
    "symbol.mp3",
    "biography.mp3",
    "guilt.mp3",
    "absorption.mp3",
)


class TestDisk(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_song_index(self):
        index = 2
        disk = Disk(SONGS, SONGS[2])
        self.assertEqual(index, disk.song_index)

        disk = Disk(SONGS)
        self.assertEqual(0, disk.song_index)

    def test_song_mp3(self):
        disk = Disk(SONGS)
        song_mp3 = disk.song_mp3
        self.assertEqual(song_mp3, SONGS[0])

    def test_song_path(self):
        path = os.path.join('songs', SONGS[0])
        disk = Disk(SONGS)
        song_path = os.path.join('songs', SONGS[disk.song_index])
        self.assertEqual(path, song_path)

    def move_song_index(self):
        index = 0
        disk = Disk(SONGS)
        disk.next()
        index += 1
        self.assertEqual(disk._playing_index, index)

        disk.prev()
        index -= 1
        self.assertEqual(index, disk._playing_index)

        disk.prev()
        index = len(SONGS)
        self.assertEqual(index, disk._playing_index)

        disk.next()
        index = 0
        self.assertEqual(index, disk._playing_index)

    def test_user_pick(self):
        disk = Disk(SONGS)
        pick = 3
        disk.user_pick(pick)
        self.assertEqual(pick, disk._playing_index)

        with self.assertRaises(IndexError):
            pick = -2
            disk.user_pick(pick)
            pick = len(SONGS)
            disk.user_pick(pick)

    def test_title(self):
        disk = Disk(SONGS)
        song = 'practical'
        title = disk.title()
        self.assertEqual(song, title)

    def test_getitem(self):
        index = 3
        disk = Disk(SONGS)
        expected = SONGS[index]
        output = disk[index]
        self.assertEqual(expected, output)

    def test_contains(self):
        song = SONGS[3]
        disk = Disk(SONGS)
        self.assertIn(song, disk)

    def test_len(self):
        expected = len(SONGS)
        disk = Disk(SONGS)
        output = len(disk)
        self.assertEqual(output, expected)

    def test_iter_next(self):
        disk = Disk(SONGS)
        for disk_item, song in zip(disk, SONGS):
            self.assertEqual(disk_item, song)
