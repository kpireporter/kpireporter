import argparse
import sys
import yaml

from reportcard.config import load
from reportcard.report import ReportFactory

parser = argparse.ArgumentParser(
    prog="reportcard",
    description="Something")
parser.add_argument("--config-file", type=argparse.FileType("r"),
                    default="reportcard.yaml")

args = parser.parse_args(sys.argv[1:])

conf = load(args.config_file)
output = ReportFactory(conf).create()

print(output)
