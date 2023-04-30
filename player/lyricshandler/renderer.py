import srt
import datetime
from .constants import EXTENSION

class Renderer:
    EXTENSION = EXTENSION
    def __init__(self, lyrics_file: str) -> None:
        self._lyrics_file = lyrics_file
        self._lyrics = tuple(srt.parse(self._set_lyrics()))
        self._index = 0

    def _set_lyrics(self):
        with open(self._lyrics_file, mode='r') as f:
            return f.read()

    def get_line(self, current_timestamp: datetime.timedelta):
        current_line = self._lyrics[self._index]

        if current_timestamp > current_line.end:
            self._index += 1
        elif current_timestamp > current_line.start:
            return current_line.content
