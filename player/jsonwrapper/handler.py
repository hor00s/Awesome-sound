from __future__ import annotations
import os
import json
from typing import (
    Any,
    Dict,
    Tuple,
    Optional,
    Generator,
)


__all__ = [
    'HandlerError',
    'Handler',
]


class HandlerError(Exception):
    pass


class Handler:
    def __init__(self, file: str, config: Dict[Any, Any]) -> None:
        self._file = file
        self._config = config

    def __eq__(self, __other: Handler | Dict[Any, Any]) -> bool:  # type: ignore
        if isinstance(__other, Dict):
            return self.read() == __other  # type: ignore
        elif isinstance(__other, Handler):
            return self.read() == __other.read()  # type: ignore
        return False

    def __or__(self, __other: Handler | Dict[Any, Any]) -> Dict[Any, Any]:
        data: Dict[Any, Any]
        if isinstance(__other, Handler):
            data = self.read() | __other.read()
            self._write(data)
            return data
        elif isinstance(__other, Dict):
            data = self.read() | __other
            self._write(data)
            return data

        e = f"unsupported operand type(s) for |: '{self.__class__.__name__}' and '{type(__other)}'"
        raise TypeError(e)

    def __str__(self) -> str:
        return str(self._read())

    def __repr__(self) -> str:
        return repr(f"<{self.__class__.__name__}({self.read()})>")

    def __len__(self) -> int:
        return len(self.read())

    def __bool__(self) -> bool:
        return bool(self.read())

    def __getitem__(self, i: Any) -> Any:
        return self.read()[i]

    def __setitem__(self, i: Any, v: Any) -> None:
        self.add(i, v)

    def __contains__(self, __other: Any) -> bool:
        return __other in self.read()

    def __delitem__(self, key: Any) -> None:
        self.remove_key(key)

    @property
    def file(self) -> str:
        return self._file

    def _write(self, data: Any) -> None:
        with open(self.file, mode='w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _read(self) -> Any:
        with open(self.file, mode='r') as f:
            data = json.load(f)
        for k, v in data.items():
            setattr(self, k, v)
        return data

    def _remove_entry(self) -> None:
        k: Any
        for k, _ in self.items():
            if k not in self._config:
                self.remove_key(k)

    def _add_entry(self) -> None:
        for k, v in self._config.items():
            if k not in self:
                self.add(k, v)

    def _checkout(self) -> None:
        if len(self) > len(self._config):
            self._remove_entry()
        elif len(self) < len(self._config):
            self._add_entry()

    def init(self) -> None:
        if not os.path.exists(self.file):
            self._write(self._config)
        self._checkout()

    def sync(self) -> None:
        self._checkout()

    def write(self, data: Any) -> None:
        self._write(data)

    def read(self) -> Any:
        return self._read()

    def get(self, key: Any, default: Optional[Any] = None) -> Any:
        data = self._read()
        return data.get(key, default)

    def remove_key(self, key: Any) -> None:
        data = self._read()
        del data[key]
        self._write(data)

    def edit(self, key: Any, value: Any) -> None:
        data = self._read()
        if key not in data:
            msg = f"Key `{key}` does not exist. If you want to add a key use `Handler.add`"
            raise HandlerError(msg)
        data[key] = value
        self._write(data)

    def add(self, key: Any, value: Any) -> None:
        data = self.read()
        if key in data:
            msg = f"Key `{key}` already exists. If you want to edit it use `Handler.edit`"
            raise HandlerError(msg)
        data[key] = value
        self._write(data)

    def restore_default(self) -> None:
        self.purge()
        self.init()

    def update(self, __other: Handler | Dict[Any, Any]) -> None:
        if isinstance(__other, Handler):
            data = self.read()
            data.update(__other.read())
            self.write(data)
        elif isinstance(__other, Dict):
            data = self.read()
            data.update(__other)
            self.write(data)
        else:
            raise HandlerError(f"`Handler.update` does not support `{type(__other)}`")

    def purge(self) -> None:
        os.remove(self.file)

    def clear(self) -> None:
        self.write({})

    def keys(self) -> Generator[Tuple[int, str], None, None]:
        yield from self.read().keys()

    def values(self) -> Generator[Tuple[int, str], None, None]:
        yield from self.read().values()

    def items(self) -> Generator[Tuple[int, str], None, None]:
        yield from self.read().items()
