import unittest
import datetime
from lyricshandler.renderer import Renderer

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
"""


class TestRenderer(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.renderer = Renderer(lyrics)

    def get_timestamp(self, time: str) -> datetime.timedelta:
        time_format = "%H:%M:%S.%f"
        time = datetime.datetime.strptime(time, time_format)
        zero_time = datetime.datetime.strptime("00:00:00.000", time_format)
        return time - zero_time

    def test_get_line(self):
        current_time = self.get_timestamp('00:00:00.000')
        before_start = self.renderer.get_line(current_time)
        self.assertIsNone(before_start)

        current_time = self.get_timestamp('00:00:06.100')
        line = self.renderer.get_line(current_time)
        self.assertEqual(line, "But you can't imagine")
