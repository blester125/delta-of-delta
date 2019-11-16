# Delta Of Delta Encoding

[![Build Status](https://travis-ci.com/blester125/delta-of-delta.svg?branch=master)](https://travis-ci.com/blester125/delta-of-delta)

[![Actions Status](https://github.com/blester125/delta-of-delta/workflows/Unit%20Test/badge.svg)](https://github.com/blester125/delta-of-delta/actions)

This has simple implementation of various ways to encoding timestamps used in time series databases.

Run `delta-of-delta-demo` to see examples of the output.

## Timestamp Encoding

This is the simplest encoding scheme, in this one we just store the timestamps. This is inefficient
because the raw bytes of successive timestamps change very little over time.

This can be used with the `timestamp_encode` function or used when streaming data with the `Encoder` class.

Example:

 * Input
   * `[1496163646, 1496163676, 1496163706, 1496163735, 1496163765]`
 * Output
   * `[1496163646, 1496163676, 1496163706, 1496163735, 1496163765]`


## Delta Encoding

This scheme stores the initial timestamp and the differences between them. This helps because we use less
memory to store the delta instead of the whole timestamp

This can be used with the `delta_encode` function or used when streaming with the `DeltaEncoder` class.

Example:

 * Input
   * `[1496163646, 1496163676, 1496163706, 1496163735, 1496163765]`
 * Output
   * `[1496163646, +30, +30, +29, +30]`


## Delta of Delta Encoding

This scheme is based on Facebook's Gorilla time-series database and is also found in Prometheus. In this case
we know use the fact that we know that most entries come in at a constant rate (because we are collecting
metrics) we only store the delta of the time between this timestamp and the previous timestamp and the
time between the previous timestamp and the one before that. Most of the data coming in will be zeros
and therefore we will get a high compression rate.

This can be used with the `delta_of_delta_encode` function or when streaming with the `DeltaOfDeltaEncoder`.

Example:

 * Input
   * `[1496163646, 1496163676, 1496163706, 1496163735, 1496163765]`
 * Output
   * `[1496163646, +30, 0, -1, +1]`


### The Encoder and Decoder classes

The Encoder and Decoder classes are stateful encoders and decoder that can be used to handle streaming
timestamps. The Encoder will record your initial timestamp in `.initial_timestamp` for easy decoding. You
initialize these classes with a timestamp and then as you pass in a new timestamp it will return the
encoded/decoded representation.

### The Encoding dataclass

The Encoding data class is a data structure that represents the timestamp stream encoded in some format.
They all have `.initial_timestamp` property that holds the first timestamp in the series and then a
second property that is a list of the following values. (called `.timestamps`, `.deltas`, and
`delta_of_deltas` respectively).
