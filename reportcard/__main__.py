import argparse
from datetime import datetime
import sys

from reportcard.config import load
from reportcard.report import ReportFactory


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

args = parser.parse_args(sys.argv[1:])

conf = load(args.config_file)

if args.start_date:
    conf.update(start_date=args.start_date)

output = ReportFactory(conf).create()

print(output)
