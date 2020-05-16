#!/usr/bin/env python
import argparse
from enum import Enum
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import sys


GLOBAL_DEFAULTS = dict(
    start_date=None,
    end_date=None,
    interval=60,
    period=60*60*24
)


def get_timeseries(start_date, end_date, interval):
    end = end_date or datetime.now()
    start = start_date or (end - timedelta(days=7))
    t = np.arange(int(start.timestamp()), int(end.timestamp()), interval)
    ts = pd.DataFrame(t, columns=['time'])
    ts['time'] = pd.to_datetime(ts['time'], unit='s')
    return ts['time'].to_numpy(dtype='datetime64[s]'), ts


SINUSOIDAL_DEFAULTS = dict(
    base=1000.0,
    amplitude=50.0,
    noise_ratio=0.1
)


def generate_sinusoidal(start_date=None, end_date=None,
                        interval=GLOBAL_DEFAULTS['interval'],
                        period=GLOBAL_DEFAULTS['period'],
                        base=SINUSOIDAL_DEFAULTS['base'],
                        amplitude=SINUSOIDAL_DEFAULTS['amplitude'],
                        noise_ratio=SINUSOIDAL_DEFAULTS['noise_ratio']):
    t, ts = get_timeseries(start_date, end_date, interval)
    pure = np.sin((2 * np.pi) * (t.astype('uint') / period))
    noise = np.random.normal(0, 1, pure.shape)
    # Normalize to [0, 1]
    pure = (1 + pure) / 2
    ts['value'] = base + (amplitude * (pure + (noise * noise_ratio)))
    return ts


class OrganicTrendType(Enum):
    INCREASING = 1
    DECREASING = 2
    RANDOM = 3


ORGANIC_DEFAULTS = dict(
    probability=0.1,
    trend=OrganicTrendType.INCREASING
)


# TODO: this roughly models "organic" behavior with some probability.
# Add a generator that can generate sinusoidal data to replicate another
# kind of "organic" pattern that is more periodic in nature (e.g., for
# events that are more likely to happen at certain times of day.)
def generate_organic(start_date=None, end_date=None,
                     interval=GLOBAL_DEFAULTS['interval'],
                     period=GLOBAL_DEFAULTS['period'],
                     probability=ORGANIC_DEFAULTS['probability'],
                     trend=ORGANIC_DEFAULTS['trend']):
    rng = np.random.default_rng()

    t, ts = get_timeseries(start_date, end_date, interval)
    num_samples = len(t)
    bucket_size = int(period / interval)
    num_buckets = int(num_samples / bucket_size)

    weights = np.arange(num_buckets)
    # Normalize so sum of all weights is 1
    weights = weights/weights.sum(0)
    if trend == OrganicTrendType.DECREASING:
        weights = np.flip(weights)
    elif trend == OrganicTrendType.RANDOM:
        rng.shuffle(weights)

    weights = np.concatenate([
        np.full(bucket_size, w / bucket_size) for w in weights])
    if len(weights) < num_samples:
        zeros = np.zeros(num_samples - len(weights))
        weights = np.concatenate((weights, zeros), axis=None)

    choice = rng.choice(
        t, round(num_samples * probability), p=weights, replace=False)

    # Check for which 't' values an event was chosen; we can assume unique
    # because we used replace=False in the choice function.
    ts['value'] = np.in1d(t, np.sort(choice), assume_unique=True)
    return ts


def main(argv):
    def simple_date(datestr):
        return datetime.strptime(datestr, "%Y-%m-%d")

    parser = argparse.ArgumentParser(
        description=("Outputs an ordered time series of events between a given"
                     "time range. The likelihood of an event occurring at a"
                     "point in time is controlled by a simple probability, "
                     "which can be automatically adjusted to increase or "
                     "decrease over time."))
    parser.add_argument("--start-date", type=simple_date,
                        help=(""))
    parser.add_argument("--end-date", type=simple_date,
                        help=(""))
    parser.add_argument("--interval", type=int,
                        default=GLOBAL_DEFAULTS['interval'],
                        help=("Interval in seconds between event candidates"))
    parser.add_argument("--period", type=int,
                        default=GLOBAL_DEFAULTS['period'],
                        help=(""))

    subparsers = parser.add_subparsers()

    organic_parser = subparsers.add_parser("organic", help=(""))
    organic_parser.add_argument("--probability", type=float,
                                default=ORGANIC_DEFAULTS['probability'],
                                help=("Starting probability for a positive "
                                      "event. Values should be [0,1]."))
    organic_parser.add_argument("--trend", type=OrganicTrendType,
                                default=ORGANIC_DEFAULTS['trend'],
                                choices=list(OrganicTrendType),
                                help=(""))
    organic_parser.set_defaults(fn=generate_organic)

    sine_parser = subparsers.add_parser("sinusoidal", help=(""))
    sine_parser.add_argument("--base", type=float,
                             default=SINUSOIDAL_DEFAULTS['base'],
                             help=(""))
    sine_parser.add_argument("--amplitude", type=float,
                             default=SINUSOIDAL_DEFAULTS['amplitude'],
                             help=(""))
    sine_parser.add_argument("--noise-ratio", type=float,
                             default=SINUSOIDAL_DEFAULTS['noise_ratio'],
                             help=(""))
    sine_parser.set_defaults(fn=generate_sinusoidal)

    args = parser.parse_args(sys.argv[1:])

    print("\n".join(f"{a}\t{b}" for a, b in args.fn(**args)))


if __name__ == "__main__":
    main(sys.argv[1::])
