from datetime import timedelta
from typing import (
    Generator,
    Any,
)


class Subtitle:
    start: timedelta
    end: timedelta
    content: str


def parse(
    str: str,
    ignore_errors: bool = False,
) -> Generator[Subtitle, Any, None]: ...
