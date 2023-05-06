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

    def test_song_index(self) -> None:
        index = 2
        disk = Disk(SONGS, SONGS[2])
        self.assertEqual(index, disk.song_index)

        disk = Disk(SONGS)
        self.assertEqual(0, disk.song_index)

    def test_song_mp3(self) -> None:
        disk = Disk(SONGS)
        song_mp3 = disk.song_mp3
        self.assertEqual(song_mp3, SONGS[0])

    def test_song_path(self) -> None:
        path = os.path.join('songs', SONGS[0])
        disk = Disk(SONGS)
        song_path = os.path.join('songs', SONGS[disk.song_index])
        self.assertEqual(path, song_path)

    def move_song_index(self) -> None:
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

    def test_user_pick(self) -> None:
        disk = Disk(SONGS)
        pick = 3
        disk.user_pick(pick)
        self.assertEqual(pick, disk._playing_index)

        with self.assertRaises(IndexError):
            pick = -2
            disk.user_pick(pick)
            pick = len(SONGS)
            disk.user_pick(pick)

    def test_title(self) -> None:
        disk = Disk(SONGS)
        song = 'practical'
        title = disk.title()
        self.assertEqual(song, title)

    def test_getitem(self) -> None:
        index = 3
        disk = Disk(SONGS)
        expected = SONGS[index]
        output = disk[index]
        self.assertEqual(expected, output)

    def test_contains(self) -> None:
        song = SONGS[3]
        disk = Disk(SONGS)
        self.assertIn(song, disk)

    def test_len(self) -> None:
        expected = len(SONGS)
        disk = Disk(SONGS)
        output = len(disk)
        self.assertEqual(output, expected)

    def test_iter_next(self) -> None:
        disk = Disk(SONGS)
        for disk_item, song in zip(disk, SONGS):
            self.assertEqual(disk_item, song)


class TestMusicPlayer(unittest.TestCase):
    def setUp(self) -> None:
        disk = Disk(SONGS)
        self.player = MusicPlayer(disk, False, 100)
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_mute(self) -> None:
        self.assertFalse(self.player.is_muted)
        self.player.mute()
        self.assertTrue(self.player.is_muted)
        self.player.mute()
        self.assertTrue(self.player.is_muted)
        self.player.unmute()
        self.assertFalse(self.player.is_muted)
        self.player.unmute()
        self.assertFalse(self.player.is_muted)

    def test_set_volume(self) -> None:
        volume = 50.0
        self.player.set_volume(volume)  # type: ignore
        self.assertEqual(self.player.volume, volume)
        with self.assertRaises(PlayerError):
            self.player.set_volume(-2)
            self.player.set_volume(101)

    def test_playing(self) -> None:
        expected = self.player.is_playing
        self.player.playing()
        self.assertIs(expected, not self.player.is_playing)

        self.player.playing()
        self.assertIs(expected, self.player.is_playing)

    def test_bool(self) -> None:
        expected = self.player._is_playing
        output = bool(self.player)
        self.assertIs(expected, output)
        self.player._is_playing = False
        expected = bool(self.player)
        self.assertIs(self.player._is_playing, expected)

    def test_change_disk(self) -> None:
        more_songs = list(SONGS)
        more_songs.append('something.mp3')
        more_songs.append('otherother.mp3')
        current_playing = self.player.disk.song_mp3
        new_disk = Disk(tuple(more_songs))
        self.player.change_disk(new_disk)
        self.assertEqual(len(self.player.disk), len(more_songs))
        playing_after_change = self.player.disk.song_mp3

        self.assertEqual(current_playing, playing_after_change)
        self.assertEqual(more_songs[self.player.disk.song_index], self.player.disk.song_mp3)

        # Check deletion
        more_songs.remove(self.player.disk.song_mp3)
        disk = Disk(tuple(more_songs))
        current_playing_index = self.player.disk.song_index
        self.player.change_disk(disk, deletetion=True)
        expected = current_playing_index + 1
        self.assertEqual(self.player.disk.song_index, expected)

        with self.assertRaises(PlayerError):
            self.player.change_disk(str())  # type: ignore
