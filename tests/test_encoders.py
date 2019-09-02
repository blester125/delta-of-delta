import random
from unittest.mock import patch
from delta_of_delta import (
    encode,
    timestamp_encode,
    delta_encode,
    delta_of_delta_encode,
    decode,
    timestamp_decode,
    delta_of_delta_decode,
    delta_decode,
    EncodingScheme,
    Encoding,
    DeltaEncoding,
    DeltaOfDeltaEncoding,
    Encoder,
    DeltaEncoder,
    DeltaOfDeltaEncoder,
    Decoder,
    DeltaDecoder,
    DeltaOfDeltaDecoder,
)


TRIALS = 100


def generate_timestamps():
    start = -1
    ts = []
    for _ in range(random.randint(10, 20)):
        ts.append(random.randint(start + 1, start + 30))
        start = ts[-1]
    return ts


def test_delta_of_delta_round_trip():
    def test():
        ts = generate_timestamps()
        res = delta_of_delta_decode(delta_of_delta_encode(ts))
        assert res == ts

    for _ in range(TRIALS):
        test()


def test_delta_round_trip():
    def test():
        ts = generate_timestamps()
        res = delta_decode(delta_encode(ts))
        assert res == ts

    for _ in range(TRIALS):
        test()


def test_timestamp_round_trip():
    def test():
        ts = generate_timestamps()
        res = timestamp_decode(timestamp_encode(ts))
        assert res == ts

    for _ in range(TRIALS):
        test()


def test_encode_dispatch_timestamp():
    def test():
        ts = generate_timestamps()
        with patch('delta_of_delta.delta_of_delta.timestamp_encode') as enc_patch:
            encode(ts, EncodingScheme.Timestamp)
            enc_patch.assert_called_once_with(ts)

    for _ in range(TRIALS):
        test()


def test_encode_dispatch_delta():
    def test():
        ts = generate_timestamps()
        with patch('delta_of_delta.delta_of_delta.delta_encode') as enc_patch:
            encode(ts, EncodingScheme.Delta)
            enc_patch.assert_called_once_with(ts)

    for _ in range(TRIALS):
        test()


def test_encode_dispatch_delta_of_delta():
    def test():
        ts = generate_timestamps()
        with patch('delta_of_delta.delta_of_delta.delta_of_delta_encode') as enc_patch:
            encode(ts, EncodingScheme.DeltaOfDelta)
            enc_patch.assert_called_once_with(ts)

    for _ in range(TRIALS):
        test()


def test_decode_dispatch_timestamp():
    def test():
        enc = Encoding(None, None)
        with patch('delta_of_delta.delta_of_delta.timestamp_decode') as dec_patch:
            decode(enc)
            dec_patch.assert_called_once_with(enc)

    for _ in range(TRIALS):
        test()


def test_decode_dispatch_delta():
    def test():
        enc = DeltaEncoding(None, None)
        with patch('delta_of_delta.delta_of_delta.delta_decode') as dec_patch:
            decode(enc)
            dec_patch.assert_called_once_with(enc)

    for _ in range(TRIALS):
        test()


def test_decode_dispatch_delta_of_delta():
    def test():
        enc = DeltaOfDeltaEncoding(None, None)
        with patch('delta_of_delta.delta_of_delta.delta_of_delta_decode') as dec_patch:
            decode(enc)
            dec_patch.assert_called_once_with(enc)

    for _ in range(TRIALS):
        test()


def test_timestamp_encoder():
    def test():
        ts = random.randint(1000, 1000000)
        enc = Encoder(None)
        res = enc.encode(ts)
        assert res == ts

    for _ in range(TRIALS):
        test()


def test_timestamp_decoder():
    def test():
        ts = random.randint(1000, 1000000)
        dec = Decoder(None)
        res = dec.decode(ts)
        assert res == ts

    for _ in range(TRIALS):
        test()


def test_delta_encoder():
    def test():
        ts = random.randint(1000, 1000000)
        gold_delta = random.randint(1, 31)
        second_ts = ts + gold_delta

        enc = DeltaEncoder(ts)
        res = enc.encode(second_ts)
        assert res == gold_delta

    for _ in range(TRIALS):
        test()


def test_delta_decoder():
    def test():
        ts = random.randint(1000, 1000000)
        delta = random.randint(1, 31)
        gold_ts = ts + delta

        dec = DeltaDecoder(ts)
        res = dec.decode(delta)
        assert res == gold_ts

    for _ in range(TRIALS):
        test()


def test_delta_of_delta_encoder():
    def test():
        ts = random.randint(1000, 1000000)
        prev_delta = random.randint(1, 31)

        delta_of_delta = random.randint(-3, 3)

        enc = DeltaOfDeltaEncoder(ts)
        enc.prev_ts = ts
        enc.prev_delta = prev_delta

        new_ts = ts + prev_delta + delta_of_delta

        res = enc.encode(new_ts)
        assert res == delta_of_delta

    for _ in range(TRIALS):
        test()


def test_delta_of_delta_decoder():
    def test():
        ts = random.randint(1000, 1000000)
        prev_delta = random.randint(1, 31)

        delta_of_delta = random.randint(-3, 3)

        dec = DeltaOfDeltaDecoder(ts)
        dec.prev_ts = ts
        dec.prev_delta = prev_delta

        gold_ts = ts + prev_delta + delta_of_delta

        res = dec.decode(delta_of_delta)
        assert res == gold_ts

    for _ in range(TRIALS):
        test()
