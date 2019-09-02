from enum import Enum
from itertools import chain
from dataclasses import dataclass
from typing import List, Union, Any, Optional


EncodingScheme = Enum("EncodingScheme", "Timestamp Delta DeltaOfDelta")


class Encoder:
    """Base class for encoding timestamps."""
    def __init__(self, timestamp):
        super().__init__()
        # Save the initial timestamp in your stream so that you can decode
        self._inital_ts = timestamp

    @property
    def initial_timestamp():
        return self._inital_ts

    def encode(self, timestamp: int) -> int:
        """Pass the timestamp as is for the most naive encoding."""
        return timestamp


class DeltaEncoder(Encoder):
    """Stream Encoder that outputs deltas between timestamps."""
    def __init__(self, timestamp: int):
        super().__init__(timestamp)
        self.prev_ts = timestamp

    def encode(self, timestamp: int) -> int:
        """Return the delta between this timestamp and the last."""
        delta = timestamp - self.prev_ts
        self.prev_ts = timestamp
        return delta


class DeltaOfDeltaEncoder(DeltaEncoder):
    """Stream Encoder that outputs the delta of delta encoding.

    The output of this is the delta between the difference between
    the most recent timestamp (t_n) and the previous timestamp (t_n-1)
    and the difference between t_n-1 and t_n-2.

    delta of delta = (t_n - t_n-1) - (t_n-1 - t_n-2)
    """
    def __init__(self, timestamp: int):
        super().__init__(timestamp)
        self.prev_delta = 0

    def encode(self, timestamp: int) -> int:
        """Return the delta of delta between the current and previous timestamp."""
        delta = timestamp - self.prev_ts
        delta_of_delta = delta - self.prev_delta
        self.prev_delta = delta
        self.prev_ts = timestamp
        return delta_of_delta


class Decoder:
    """Base case for the streaming timestamp decoder."""
    def __init__(self, *args, **kwargs):
        super().__init__()

    def decode(self, timestamp: int) -> int:
        """Pass through the timestamp of simple encoding."""
        return timestamp


class DeltaDecoder(Decoder):
    """The steam decoder for delta encoded streams."""
    def __init__(self, timestamp: int):
        super().__init__()
        self.prev_ts = timestamp

    def decode(self, delta: int) -> int:
        """Return the timestamp that is delta away from the previous timestamp."""
        self.prev_ts += delta
        return self.prev_ts


class DeltaOfDeltaDecoder(DeltaDecoder):
    """The stream decoder for the delta of delta decoding."""
    def __init__(self, timestamp: int):
        super().__init__(timestamp)
        self.prev_delta = 0

    def decode(self, delta_of_delta: int) -> int:
        """Return the next timestamp.

        curr_timestamp = prev_timestamp + prev_delta + delta_of_delta
        """
        self.prev_delta += delta_of_delta
        self.prev_ts += self.prev_delta
        return self.prev_ts


@dataclass
class Encoding:
    """A output data struct. Saves the initial timestamp to match the other formats."""
    initial_timestamp: int
    values: List[int]

    @property
    def timestamps(self):
        return self.values

    def __str__(self):
        return f"[{', '.join(map(str, chain((self.initial_timestamp,), self.timestamps)))}]"


@dataclass
class DeltaEncoding(Encoding):
    """The initial timestamp and deltas to represent a delta encoded stream."""
    @property
    def deltas(self):
        return self.values

    def __str__(self):
        offsets = (f"+{d}" if d > 0 else str(d) for d in self.deltas)
        return f"[{', '.join(chain((str(self.initial_timestamp),), offsets))}]"


@dataclass
class DeltaOfDeltaEncoding(DeltaEncoding):
    """The initial timestamps and delta of delta to represent a delta of delta encoded stream.

    The inital delta of deltas is the delta compared to 0 and is often much larger than the other delta of deltas
    """
    @property
    def delta_of_deltas(self):
        return self.values

    def __str__(self):
        offsets = (f"+{d}" if d > 0 else str(d) for d in self.delta_of_deltas)
        return f"[{', '.join(chain((str(self.initial_timestamp),), offsets))}]"


def encode(timestamps: List[int], scheme: Optional[EncodingScheme] = None) -> Encoding:
    """Encode a list of timestamps. Encoding scheme enum is used for dispatch."""
    if scheme is EncodingScheme.Timestamp:
        return timestamp_encode(timestamps)
    if scheme is EncodingScheme.Delta:
        return delta_encode(timestamps)
    return delta_of_delta_encode(timestamps)


def _encode(timestamps: List[int], encoder: Encoder, encoding: Encoding) -> Encoding:
    """Generic encoder using subclasses to encode in different formats.

    It works by creating an encoder class which is stateful, It is initialized
    to the first timestamp and encode is called on each timestamp in the series.
    IT returns an encoding data structure that can be used to decode to the
    original formats.
    """
    enc = encoder(timestamps[0])
    tss = [enc.encode(ts) for ts in timestamps[1:]]
    return encoding(timestamps[0], tss)


def delta_of_delta_encode(timestamps: List[int]) -> DeltaOfDeltaEncoding:
    """Encode timestamps as delta of delta offsets."""
    return _encode(timestamps, DeltaOfDeltaEncoder, DeltaOfDeltaEncoding)


def delta_encode(timestamps: List[int]) -> DeltaEncoding:
    """Encode timestamps as delta offsets."""
    return _encode(timestamps, DeltaEncoder, DeltaEncoding)


def timestamp_encode(timestamps: List[int]) -> List[int]:
    """Encode timestamps as timestamps (actually just a passthrough)."""
    return _encode(timestamps, Encoder, Encoding)


def decode(encoding: Encoding) -> List[int]:
    """Decode the encoded timestamps to timestamps. Dispatch is done via the encoding data structure type."""
    if isinstance(encoding, DeltaOfDeltaEncoding):
        return delta_of_delta_decode(encoding)
    if isinstance(encoding, DeltaEncoding):
        return delta_decode(encoding)
    return timestamp_decode(encoding)


def _decode(encoding: Encoding, decoder: Decoder) -> List[int]:
    """Generic decoder using subcalsses to decode different formats.

    It works by nitializing a list of timestamps and the decoder  with the
    initial timestamp from the encoding data structure. The stateful decoder
    is then called on all the values in the output.
    """
    tss = [encoding.initial_timestamp]
    dec = decoder(encoding.initial_timestamp)
    for v in encoding.values:
        tss.append(dec.decode(v))
    return tss


def delta_of_delta_decode(dode: DeltaOfDeltaEncoding) -> List[int]:
    """Decode delta of delta encoded timestamps back to a list of timestamps."""
    return _decode(dode, DeltaOfDeltaDecoder)


def delta_decode(de: DeltaEncoding) -> List[int]:
    """Decode delta encoded timestamps back to a list of timestamps."""
    return _decode(de, DeltaDecoder)


def timestamp_decode(e: Encoding) -> List[int]:
    """Decode timestamp encoded timestamps back to a list of timestamps. (Really just a passthrough.)"""
    return _decode(e, Decoder)


def main():
    """Showcase of the different encoding schemes."""
    timestamps = [1496163646, 1496163676, 1496163706, 1496163735, 1496163765]
    print(f"Timestamps:              {timestamps}")
    ts = timestamp_encode(timestamps)
    print(f"Timestamp Encoding:      {ts}")
    d = delta_encode(timestamps)
    print(f"Delta Encoding:          {d}")
    dod = delta_of_delta_encode(timestamps)
    print(f"Delta of Delta Encoding: {dod}")


if __name__ == "__main__":
    main()
