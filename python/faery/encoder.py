from __future__ import annotations

import collections.abc
import pathlib
import typing

import numpy

from . import common

if typing.TYPE_CHECKING:
    from . import aedat  # type: ignore
    from . import dat  # type: ignore
    from . import event_stream  # type: ignore
    from . import evt  # type: ignore
else:
    from .faery import aedat
    from .faery import dat
    from .faery import event_stream
    from .faery import evt


def save(
    stream: collections.abc.Iterable[numpy.ndarray],
    path: typing.Union[pathlib.Path, str],
    dimensions: tuple[int, int],
    version: typing.Optional[
        typing.Literal["dat1", "dat2", "evt2", "evt2.1", "evt3"]
    ] = None,
    zero_t0: bool = True,
    compression: typing.Optional[
        typing.Tuple[typing.Literal["lz4", "zstd"], int]
    ] = aedat.LZ4_DEFAULT,
    file_type: typing.Optional[common.FileType] = None,
) -> str:
    """Writes the stream to an event file (supports .aedat4, .es, .raw, and .dat).

    version is only used if the file type is EVT (.raw) or DAT.

    zero_t0 is only used if the file type is ES, EVT (.raw) or DAT.
    The original t0 is stored in the header of EVT and DAT files, and is discarded if the file type is ES.

    compression is only used if the file type is AEDAT.

    Args:
        stream: An iterable of event arrays (structured arrays with dtype faery.DVS_DTYPE).
        path: Path of the output event file.
        dimensions: Width and height of the sensor.
        version: Version for EVT (.raw) and DAT files. Defaults to "dat2" for DAT and "evt3" for EVT.
        zero_t0: Whether to normalize timestamps and write the offset in the header for EVT (.raw) and DAT files. Defaults to True.
        compression: Compression for aedat files. Defaults to ("lz4", 1).
        file_type: Override the type determination algorithm. Defaults to None.

    Returns:
        The original t0 as a timecode if the file type is ES, EVT (.raw) or DAT, and if `zero_t0` is true. 0 as a timecode otherwise.
        To reconstruct the original timestamps when decoding ES files with Faery, pass the returned value to `faery.stream_from_file`.
        EVT (.raw) and DAT files do not need this (t0 is written in their header), but it is returned here anyway for compatibility
        with software than do not support the t0 header field.
    """
    path = pathlib.Path(path)
    file_type = common.FileType.guess(path) if file_type is None else file_type
    if file_type == common.FileType.AEDAT:
        with aedat.Encoder(
            path,
            description_or_tracks=[
                aedat.Track(id=0, data_type="events", dimensions=dimensions),
            ],
            compression=compression,
        ) as encoder:
            for events in stream:
                encoder.write(0, events)
            t0 = 0
    elif file_type == common.FileType.DAT:
        with dat.Encoder(
            path,
            version="dat2" if version is None else version,  # type: ignore
            event_type="cd",
            zero_t0=zero_t0,
            dimensions=dimensions,
        ) as encoder:
            for events in stream:
                events = events.astype(
                    dtype=numpy.dtype(
                        [
                            ("t", "<u8"),
                            ("x", "<u2"),
                            ("y", "<u2"),
                            ("payload", "u1"),
                        ]
                    ),
                    casting="unsafe",
                    copy=False,
                )
                encoder.write(events)
            t0_candidate = encoder.t0()
            if t0_candidate is None:
                t0 = 0
            else:
                t0 = t0_candidate
    elif file_type == common.FileType.ES:
        with event_stream.Encoder(
            path,
            event_type="dvs",
            zero_t0=zero_t0,
            dimensions=dimensions,
        ) as encoder:
            for events in stream:
                events["y"] = dimensions[1] - 1 - events["y"]
                encoder.write(events)
            t0_candidate = encoder.t0()
            if t0_candidate is None:
                t0 = 0
            else:
                t0 = t0_candidate
    elif file_type == common.FileType.EVT:
        with evt.Encoder(
            path,
            version="evt3" if version is None else version,  # type: ignore
            zero_t0=zero_t0,
            dimensions=dimensions,
        ) as encoder:
            for events in stream:
                encoder.write({"events": events})
            t0_candidate = encoder.t0()
            if t0_candidate is None:
                t0 = 0
            else:
                t0 = t0_candidate
    else:
        raise Exception(f"file type {file_type} not implemented")
    return common.timestamp_to_timecode(t0)
