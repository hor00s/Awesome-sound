import srt  # type: ignore
import datetime
from typing import Union, Optional
from .constants import EXTENSION


__all__ = (
    'Renderer',
)


class Renderer:
    EXTENSION = EXTENSION

    def __init__(self, lyrics_file: str) -> None:
        self._lyrics_file = lyrics_file
        self._lyrics = tuple(srt.parse(self._set_lyrics()))
        self._index = 0

    def _set_lyrics(self) -> str:
        try:
            with open(self._lyrics_file, mode='r') as f:
                return f.read()
        except FileNotFoundError:
            return self._lyrics_file

    def get_line(self, current_timestamp: datetime.timedelta,
                 delay: Optional[float]) -> Union[str, None]:
        # Not the most efficient way but it'll do for now
        delay_to_td = datetime.timedelta(seconds=delay or 0)
        lyrics_sync = current_timestamp - delay_to_td

        for lyric in self._lyrics:
            if lyric.start <= lyrics_sync < lyric.end:
                return str(lyric.content)
        return None
