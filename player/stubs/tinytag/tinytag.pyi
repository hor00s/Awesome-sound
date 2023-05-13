from __future__ import annotations
from typing import Optional


class TinyTag:
    @classmethod
    def get(
        cls,
        filename: str,
        tags: bool = True,
        duration: bool = True,
        image: bool = False,
        ignore_errors: bool = False,
        encoding: Optional[str] = None,
    ) -> TinyTag: ...

    @property
    def duration(self) -> float: ...
