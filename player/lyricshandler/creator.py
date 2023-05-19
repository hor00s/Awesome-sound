import os
from comps import MusicPlayer
from .constants import EXTENSION


__all__ = (
    'Creator',
)


class Creator:
    EXTENSION = EXTENSION

    def __init__(self, player: MusicPlayer, lyrics_dir: str) -> None:
        self.song_name = player.disk.song_name
        self.lyrics_dir = lyrics_dir
        self.full_path = os.path.join(lyrics_dir, self.song_name + EXTENSION)

    def init(self) -> None:
        if not os.path.exists(self.full_path):
            with open(self.full_path, mode='w') as _:
                ...

    def manual_save(self, path: str) -> str:
        with open(path, mode='r') as f:
            content = f.read()

        save_file = os.path.join(self.lyrics_dir, self.song_name + self.EXTENSION)
        with open(save_file, mode='w') as f:
            f.write(content)
        return save_file

    def write_line(self, line: str, start: str, stop: str) -> None:
        with open(self.full_path, mode='r') as f:
            content = f.read()

        if not content:
            index = 0
        elif content:
            index = len(tuple(filter(lambda i: not i, content.split('\n'))))

        if content:
            line_format = f"""{content}
{index}
00:{start} --> 00:{stop}
{line}
"""
        else:
            line_format = f"""{index}
00:{start} --> 00:{stop}
{line}
"""

        with open(self.full_path, mode='w') as f:
            f.write(line_format)
