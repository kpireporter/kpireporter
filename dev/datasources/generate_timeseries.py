#!/usr/bin/env python
import argparse
from datetime import datetime, timedelta
import random
import sys


def simple_date(datestr):
    return datetime.strptime(datestr, "%Y-%m-%d")

def generate(start_date=None, end_date=None, interval=60, probability=0.1,
             attack=1.2, attack_interval=60*60*24):
    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        start_date = end_date - timedelta(days=7)

    # Cycle interval
    delta = timedelta(seconds=interval)

    curr_date = start_date
    cycles = 0
    entries = []
    while curr_date < end_date:
        curr_date += delta
        cycles += interval
        if random.random() < probability:
            entries.append(curr_date.strftime("%Y-%m-%d %H:%M:%S"))
        if cycles % attack_interval == 0:
            probability *= attack

    return entries

def main(argv):
    parser = argparse.ArgumentParser(
        description=("Outputs an ordered time series of events between a given"
                    "time range. The likelihood of an event occurring at a"
                    "point in time is controlled by a simple probability, which"
                    "can be automatically adjusted to increase/decrease over"
                    "time."))
    parser.add_argument("--start_date", type=simple_date,
                        default=datetime.now(), help=(""))
    parser.add_argument("--end_date", type=simple_date,
                        default=datetime.now() + timedelta(days=7),
                        help=(""))
    parser.add_argument("--interval", type=int,
                        help=("Interval in seconds between event candidates"))
    parser.add_argument("--attack", type=float,
                        help=("Probability multiplier on attack. A value of 1 "
                            "effectively disables the attack."))
    parser.add_argument("--attack_interval", type=int,
                        help=("Interval in seconds between attacks"))
    parser.add_argument("--probability", type=float,
                        help=("Starting probability for a positive event. Values "
                            "should be [0,1]."))

    args = parser.parse_args(sys.argv[1:])
    print("\n".join(generate(**args)))

if __name__ == "__main__":
    main(sys.argv[1::])