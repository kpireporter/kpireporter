#!/usr/bin/env python
import os

from ..generate_timeseries import generate

dirpath = os.path.dirname(os.path.realpath(__file__))

def open_file(name, mode):
    return open(os.path.join(dirpath, name), mode)

def make():
    with open_file("signups.sql.tpl", "r") as f:
        template = f.read()
        values = [f'("{v}")' for v in generate()]
        values = f'{",".join(values)};'
    with open_file("signups.sql", "w") as f:
        f.write(template.format(values=values))