import argparse
from datetime import datetime
import logging
import sys
from timeit import default_timer as timer

from reportcard.config import load
from reportcard.report import ReportFactory

logging.basicConfig(level=logging.DEBUG)

def simple_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Not a valid date: {date_str}")


parser = argparse.ArgumentParser(
    prog="reportcard",
    description="Something")
parser.add_argument("--config-file", type=argparse.FileType("r"),
                    default="reportcard.yaml")
parser.add_argument("--start-date", type=simple_date)
parser.add_argument("--end-date", type=simple_date)
parser.add_argument("--theme-dir", default="/etc/reportcard/theme")

args = parser.parse_args(sys.argv[1:])

conf = load(args.config_file)

if args.start_date:
    conf.update(start_date=args.start_date)
if args.end_date:
    conf.update(end_date=args.end_date)

start = timer()

ReportFactory(conf).create()

end = timer()
print(f"Generated report in {(end - start) * 1000:.2f}ms.")
