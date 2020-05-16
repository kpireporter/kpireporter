#!/usr/bin/env python
from datetime import datetime, timedelta
import os

from ..generate_timeseries import generate_organic

dirpath = os.path.dirname(os.path.realpath(__file__))


def open_file(name, mode):
    return open(os.path.join(dirpath, name), mode)


def mysql_date_format(datestr):
    return datetime.strftime(datestr, format='%Y-%m-%d %H:%M:%S')


def make():
    end_date = datetime.now()
    # Generate 2 weeks of data for comparison queries
    start_date = end_date - timedelta(days=14)

    with open_file("signups.sql.tpl", "r") as f:
        template = f.read()
        ts_data = generate_organic(start_date=start_date, end_date=end_date)
        values = [
            f'("{mysql_date_format(v)}")'
            for v in ts_data[ts_data['value']]['time']
        ]
    with open_file("signups.sql", "w") as f:
        f.write(template.format(values=f'{",".join(values)};'))
