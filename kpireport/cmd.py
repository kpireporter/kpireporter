import argparse
from datetime import datetime
from itertools import chain
import logging
import sys
from timeit import default_timer as timer

from .config import load
from .report import ReportFactory


def simple_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Not a valid date: {date_str}")


class ConfigFiles(argparse._AppendAction):
    pass


def run(argv=None):
    if not argv:
        argv = sys.argv
    parser = argparse.ArgumentParser(
        prog="kpireport", description="Something", allow_abbrev=False
    )
    parser.add_argument(
        "-c",
        "--config-file",
        type=argparse.FileType("r"),
        nargs="+",
        action="append",
        default=[],
    )
    parser.add_argument("-s", "--start-date", type=simple_date)
    parser.add_argument("-e", "--end-date", type=simple_date)
    parser.add_argument("--theme-dir", default="/etc/kpireport/theme")
    parser.add_argument("-v", "--verbose", dest="verbosity", action="count", default=0)

    args = parser.parse_args(argv[1:])

    log_level = logging.INFO
    if args.verbosity >= 2:
        log_level = logging.DEBUG
    elif args.verbosity >= 1:
        log_level = logging.DEBUG
        # Suppress DEBUG output for matplot lib by default, as it
        # is quite noisy.
        logging.getLogger("matplotlib").setLevel(logging.INFO)
    logging.basicConfig(level=log_level)

    config_files = list(chain(*args.config_file))
    if not config_files:
        config_files.append(argparse.FileType("r")("kpireport.yml"))
    conf = load(*config_files)

    if args.start_date:
        conf.update(start_date=args.start_date)
    if args.end_date:
        conf.update(end_date=args.end_date)

    start = timer()

    ReportFactory(conf).create()

    end = timer()
    print(f"Generated report in {(end - start) * 1000:.2f}ms.")
