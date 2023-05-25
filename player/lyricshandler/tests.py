import unittest
import datetime
from .renderer import Renderer
# from comps import MusicPlayer, Disk
# from .creator import Creator
from .search import (
    search_for,
    ISearch,
    LyricsSearch,
    YoutubeSearch,
)


lyrics = """
0
00:00:01,100 --> 00:00:06,000
You say you know just who I am

1
00:00:06,100 --> 00:00:08,500
But you can't imagine

2
00:00:08,600 --> 00:00:13,400
What waits for you across the line

3
00:00:13,500 --> 00:00:16,700
You thought you had me

4
00:00:16,800 --> 00:00:24,100
But I'm still here standing

5
00:00:24,200 --> 00:00:30,400
And I'm tired of backing down

6
00:00:30,500 --> 00:00:34,300
And I'm here now feeling the pain
"""


class TestRendered(unittest.TestCase):
    def setUp(self) -> None:
        self.renderer = Renderer(lyrics)
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_get_line(self) -> None:
        # ~ TESTS WITHOUT DELAY ~
        delay = 0

        # Non existing timestamp
        timestamp = datetime.timedelta(hours=0, minutes=0, seconds=0, milliseconds=0)
        output = self.renderer.get_line(timestamp, delay)
        self.assertIsNone(output)

        # Timestamp exactly at start (00:00:01,100 --> 00:00:06,000)
        expected = "You say you know just who I am"
        timestamp = datetime.timedelta(hours=0, minutes=0, seconds=1, milliseconds=100)
        output = self.renderer.get_line(timestamp, delay)
        self.assertEqual(expected, output)

        # Timestamp in between (00:00:13,500 --> 00:00:16,700)
        expected = "You thought you had me"
        timestamp = datetime.timedelta(hours=0, minutes=0, seconds=14, milliseconds=500)
        output = self.renderer.get_line(timestamp, delay)
        self.assertEqual(expected, output)

        # Timestamp exactly at the end (00:00:16,800 --> 00:00:24,100)
        expected = None  # type: ignore
        timestamp = datetime.timedelta(hours=0, minutes=0, seconds=24, milliseconds=100)
        output = self.renderer.get_line(timestamp, delay)
        self.assertIsNone(output)

        # ~ TESTS WITH DELAY ~
        delay = 3

        # Non existing timestamp
        timestamp = datetime.timedelta(hours=0, minutes=0, seconds=0 + delay, milliseconds=0)
        output = self.renderer.get_line(timestamp, delay)
        self.assertIsNone(output)

        # Timestamp exactly at start (00:00:01,100 --> 00:00:06,000)
        expected = "You say you know just who I am"
        timestamp = datetime.timedelta(hours=0, minutes=0, seconds=1 + delay, milliseconds=100)
        output = self.renderer.get_line(timestamp, delay)
        self.assertEqual(expected, output)

        # Timestamp in between (00:00:13,500 --> 00:00:16,700)
        expected = "You thought you had me"
        timestamp = datetime.timedelta(hours=0, minutes=0, seconds=14 + delay, milliseconds=500)
        output = self.renderer.get_line(timestamp, delay)
        self.assertEqual(expected, output)

        # Timestamp exactly at the end (00:00:16,800 --> 00:00:24,100)
        expected = None  # type: ignore
        timestamp = datetime.timedelta(hours=0, minutes=0, seconds=24 + delay, milliseconds=100)
        output = self.renderer.get_line(timestamp, delay)
        self.assertIsNone(output)


# class TestCreator(unittest.TestCase):
#     def setUp(self) -> None:
#         songs = (
#             'Sjaak - Trompetisto (Official Music Video)',
#             'Tiësto & Ava Max - The Motto (Official Music Video)',
#             'Tones And I - Dance Monkey (Brynny Remix)',
#         )
#         self.disk = Disk(songs)
#         self.player = MusicPlayer(self.disk, False, 80)
#         self.creator = Creator(self.player)
#         return super().setUp()

#     def tearDown(self) -> None:
#         return super().tearDown()


class TestSearch(unittest.TestCase):
    def setUp(self) -> None:
        self.ls = LyricsSearch('The Neighbourhood - Sweater Weather (Official Video)')
        self.yt = YoutubeSearch('The Neighbourhood - Sweater Weather (Official Video)')
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_lyrics_name(self) -> None:
        self.ls.song_name()
        self.assertEqual(self.ls._song_name, 'The Neighbourhood - Sweater Weather')

    def test_youtube_name(self) -> None:
        self.yt.song_name()
        self.assertEqual(self.yt._song_name, 'The Neighbourhood - Sweater Weather')

    def test_lyrics_query(self) -> None:
        self.ls.song_name().query()
        query = 'https://www.rentanadviser.com/subtitles/subtitles4songs\
.aspx?q=The%20Neighbourhood%20-%20Sweater%20Weather'
        self.assertEqual(self.ls.url, query)

    def test_yt_search(self) -> None:
        self.yt.song_name().query()
        query = 'https://www.youtube.com/results?search_query=The+Neighbourhood+-+Sweater+Weather'
        self.assertEqual(self.yt.url, query)

    def test_factory_picker(self) -> None:
        song_name = 'Sjaak - Trompetisto (Official Music Video)'
        search = search_for('lyrics', song_name)
        self.assertIsInstance(search, LyricsSearch)
        self.assertIsInstance(search, ISearch)

        search = search_for('youtube', song_name)
        self.assertIsInstance(search, YoutubeSearch)
        self.assertIsInstance(search, ISearch)
