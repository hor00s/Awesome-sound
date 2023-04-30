import os
from comps import Disk
from .constants import EXTENSION


__all__ = (
    'Creator',
)


class Creator:
    EXTENSION = EXTENSION

    def __init__(self, song: Disk, lyrics_dir: str) -> None:
        self.song = song.title()
        self.lyrics_dir = lyrics_dir

    def manual_save(self, path: str):
        with open(path, mode='r') as f:
            content = f.read()

        save_file = os.path.join(self.lyrics_dir, self.song + self.EXTENSION)
        with open(save_file, mode='w') as f:
            f.write(content)
