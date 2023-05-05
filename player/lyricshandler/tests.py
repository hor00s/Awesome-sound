import unittest
import datetime
from .renderer import Renderer


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
#         self.creator = Creator(Disk(), '')
#         return super().setUp()

#     def tearDown(self) -> None:
#         return super().tearDown()
