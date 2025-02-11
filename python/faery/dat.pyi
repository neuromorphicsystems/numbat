from __future__ import annotations

import pathlib
import typing
import types

import numpy

class Decoder:
    version: typing.Literal["dat1", "dat2"]
    event_type: typing.Literal["2d", "cd", "trigger"]
    dimensions: typing.Optional[tuple[int, int]]

    def __init__(
        self,
        path: typing.Union[pathlib.Path, str],
        dimensions_fallback: typing.Optional[tuple[int, int]] = None,
        version_fallback: typing.Optional[typing.Literal["dat1", "dat2"]] = None,
    ): ...
    def __enter__(self) -> Decoder: ...
    def __exit__(
        self,
        exception_type: typing.Optional[typing.Type[BaseException]],
        value: typing.Optional[BaseException],
        traceback: typing.Optional[types.TracebackType],
    ) -> bool: ...
    def __iter__(self) -> Decoder: ...
    def __next__(self) -> numpy.ndarray: ...

class Encoder:
    @typing.overload
    def __init__(
        self,
        path: typing.Union[pathlib.Path, str],
        version: typing.Literal["dat1", "dat2"],
        event_type: typing.Literal["2d"],
        zero_t0: bool,
        dimensions: tuple[int, int],
    ): ...
    @typing.overload
    def __init__(
        self,
        path: typing.Union[pathlib.Path, str],
        version: typing.Literal["dat1", "dat2"],
        event_type: typing.Literal["cd"],
        zero_t0: bool,
        dimensions: tuple[int, int],
    ): ...
    @typing.overload
    def __init__(
        self,
        path: typing.Union[pathlib.Path, str],
        version: typing.Literal["dat1", "dat2"],
        event_type: typing.Literal["trigger"],
        zero_t0: bool,
        dimensions: None,
    ): ...
    def __enter__(self) -> Encoder: ...
    def __exit__(
        self,
        exception_type: typing.Optional[typing.Type[BaseException]],
        value: typing.Optional[BaseException],
        traceback: typing.Optional[types.TracebackType],
    ) -> bool: ...
    def t0(self) -> typing.Optional[int]: ...
    def write(self, packet: numpy.ndarray): ...
