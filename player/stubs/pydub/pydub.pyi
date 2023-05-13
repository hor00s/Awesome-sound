from __future__ import annotations


class AudioSegment:
    @classmethod
    def from_file(
        csl,
        file: str,
        format: str,
    ) -> AudioSegment: ...
