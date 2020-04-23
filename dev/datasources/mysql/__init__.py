#!/usr/bin/env python
from datetime import datetime, timedelta
import os

from ..generate_timeseries import generate

dirpath = os.path.dirname(os.path.realpath(__file__))

def open_file(name, mode):
    return open(os.path.join(dirpath, name), mode)

def make():
    end_date = datetime.now()
    # Generate 2 weeks of data for comparison queries
    start_date = end_date - timedelta(days=14)

    with open_file("signups.sql.tpl", "r") as f:
        template = f.read()
        ts_data = generate(start_date=start_date, end_date=end_date)
        values = [f'("{v}")' for v in ts_data]
        values = f'{",".join(values)};'
    with open_file("signups.sql", "w") as f:
        f.write(template.format(values=values))