from typing import (
    Optional,
    Callable,
    Dict,
    Any,
)


class Stream:
    ...


class StreamQuery:
    fmt_streams: Any

    def get_audio_only(self, subtype: str = "mp4") -> Optional[Stream]: ...


class YouTube:
    streams: StreamQuery

    def __init__(
        self,
        url: str,
        on_progress_callback: Optional[Callable[[Any, bytes, int], None]] = None,
        on_complete_callback: Optional[Callable[[Any, Optional[str]], None]] = None,
        proxies: Optional[Dict[str, str]] = None,
        use_oauth: bool = False,
        allow_oauth_cache: bool = True,
    ) -> None: ...

    def download(
        self,
        output_path: str | None = None,
        filename: str | None = None,
        filename_prefix: str | None = None,
        skip_existing: bool = True,
        timeout: int | None = None,
        max_retries: int | None = 0
    ) -> str: ...
