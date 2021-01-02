import argparse
from datetime import datetime
from itertools import chain
from glob import glob
import logging
import os
import sys

from timeit import default_timer as timer

from .config import load, DEFAULT_CONF_DIR
from .report import ReportFactory


def simple_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Not a valid date: {date_str}")


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
    parser.add_argument("--theme-dir", default=f"{DEFAULT_CONF_DIR}/theme")
    parser.add_argument("--license-file", type=argparse.FileType("r"))
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
        for search_dir in [".", DEFAULT_CONF_DIR]:
            search_path = os.path.join(search_dir, "config.yaml")
            if os.path.isfile(search_path):
                config_files.append(open(search_path, "r"))
                break
        if not config_files:
            raise ValueError(
                (
                    "Could not find any configuration file! Use the --config-file "
                    "option when using a non-standard configuration location."
                )
            )

    conf = load(*config_files)

    if args.start_date:
        conf.update(start_date=args.start_date)
    if args.end_date:
        conf.update(end_date=args.end_date)
    if args.theme_dir:
        conf.get("theme").update(theme_dir=args.theme_dir)

    license_file = args.license_file
    if not license_file:
        matches = list(
            chain(*[glob(f"{DEFAULT_CONF_DIR}/*.{ext}") for ext in ["key", "pub"]])
        )
        if matches:
            # Use the last found file. This is helpful so that later license files
            # (if date is in the name) are used in preference to earlier ones.
            license_file = open(matches[-1], "r")
    if license_file:
        with license_file:
            license_content = license_file.read()
            conf.update(license_key="".join(license_content.split("\n")[1:-1]))

    start = timer()

    ReportFactory(conf).create()

    end = timer()
    print(f"Generated report in {(end - start) * 1000:.2f}ms.")
