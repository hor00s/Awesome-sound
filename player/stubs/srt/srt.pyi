from datetime import timedelta
from typing import (
    Generator,
    Any,
)


class Subtitle:
    start: timedelta
    end: timedelta
    content: str


class SRTParseError(Exception):
    expected_start: Any
    acrual_start: Any
    unmatched_content: Any


def parse(
    str: str,
    ignore_errors: bool = False,
) -> Generator[Subtitle, Any, None]: ...
