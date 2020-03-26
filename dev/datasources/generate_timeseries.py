#!/usr/bin/env python
import argparse
from datetime import datetime, timedelta
import random
import sys


def simple_date(datestr):
    return datetime.strptime(datestr, "%Y-%m-%d")


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
parser.add_argument("--interval", type=int, default=60,
                    help=("Interval in seconds between event candidates"))
parser.add_argument("--attack", type=float, default=1.2,
                    help=("Probability multiplier on attack. A value of 1 "
                          "effectively disables the attack."))
parser.add_argument("--attack_interval", type=int, default=60*60*24,
                    help=("Interval in seconds between attacks"))
parser.add_argument("--probability", type=float, default=0.1,
                    help=("Starting probability for a positive event. Values "
                          "should be [0,1]."))

args = parser.parse_args(sys.argv[1:])

# Cycle interval
delta = timedelta(seconds=args.interval)
# How much to increase/decrease probability of event,
# and how often to perform the adjustment.
attack = args.attack
attack_interval = args.attack_interval
# Starting probability of event
probability = args.probability

curr_date = args.start_date
cycles = 0
while curr_date < args.end_date:
    curr_date += delta
    cycles += args.interval
    if random.random() < probability:
        print(curr_date.strftime("%Y-%m-%d %H:%M:%S"))
    if cycles % attack_interval == 0:
        probability *= attack
