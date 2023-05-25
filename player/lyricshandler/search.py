from __future__ import annotations
import webbrowser
from typing import Literal
from abc import (
    ABC,
    abstractmethod,
    abstractproperty,
)


__all__ = (
    'LyricsSearch',
    'YoutubeSearch',
    'search_for',
)


class ISearch(ABC):
    @abstractmethod
    def __init__(self, song_title: str) -> None: ...

    @abstractmethod
    def __str__(self) -> str: ...

    @abstractmethod
    def __repr__(self) -> str: ...

    @abstractproperty
    def song_title(self) -> str: ...

    @abstractmethod
    def song_name(self) -> ISearch: ...

    @abstractmethod
    def query(self) -> ISearch: ...

    @abstractmethod
    def search(self) -> None: ...


class LyricsSearch(ISearch):
    def __init__(self, song_title: str) -> None:
        self.url = "https://www.rentanadviser.com/subtitles/subtitles4songs.aspx?q="
        self._song_title = song_title
        self._song_name = ""
        self._query = ""

    def __str__(self) -> str:
        return self._song_title

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.song_title})>"

    @property
    def song_title(self) -> str:
        return self._song_title

    def song_name(self) -> LyricsSearch:
        self._song_name = ""
        for i in self.song_title:
            if i == '(':
                break
            self._song_name += i
        self._song_name = self._song_name.strip()
        return self

    def query(self) -> LyricsSearch:
        self.url += '%20'.join(self._song_name.split(' ')).strip()
        return self

    def search(self) -> None:
        webbrowser.open(self.url)


class YoutubeSearch(ISearch):
    def __init__(self, song_title: str) -> None:
        self.url = "https://www.youtube.com/results?search_query="
        self._song_title = song_title
        self._song_name = ""
        self._query = ""

    def __str__(self) -> str:
        return self._song_name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self._song_name})>"

    @property
    def song_title(self) -> str:
        return self._song_title

    def song_name(self) -> ISearch:
        self._song_name = ""
        for i in self.song_title:
            if i == '(':
                break
            self._song_name += i
        self._song_name = self._song_name.strip()
        return self

    def query(self) -> ISearch:
        self.url += '+'.join(self._song_name.split(' '))
        return self

    def search(self) -> None:
        webbrowser.open(self.url)


def search_for(site: Literal['youtube', 'lyrics'], song_title: str) -> ISearch:
    return {
        'youtube': YoutubeSearch(song_title),
        'lyrics': LyricsSearch(song_title),
    }[site]


if __name__ == '__main__':
    s = YoutubeSearch('The Neighbourhood - Sweater Weather')
    s.song_name()
    (
        s.song_name()
         .query()
         .search()
    )
