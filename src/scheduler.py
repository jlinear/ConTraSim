# !/usr/bin/env python
# ConTraG, Contextual Trajectory Generator; see https://
# Copyright (C) 2020-2020 University of Notre Dame and others.
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# https://www.eclipse.org/legal/epl-2.0/
# This Source Code may also be made available under the following Secondary
# Licenses when the conditions for such availability set forth in the Eclipse
# Public License 2.0 are satisfied: GNU General Public License, version 2
# or later which is available at
# https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
# SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-or-later

# @file     scheduler.py
# @author   Jian Yang
# @date     2020-07-20

"""
Two major features are realized in this python script
1) translate a raw schedule into formatted itinerary
2) extract key info. from sample trajectory data and generate itinerary
"""

import os, sys
import pandas as pd
from pathlib import Path


def convert24(str_t):
    tail = str_t[-2:]
    h, m = str_t[:-2].strip().split(':')

    if tail in ("AM", "am") and h == "12":
        return "00" + str_t[2:-2]
    elif tail in ("AM", "am"):
        if len(h) < 2:  # allows input as "1:30am"
            return "0" + str_t[:-2]
        else:
            return str_t[:-2]
    elif tail in ("PM", "pm") and str_t[:2] == "12":
        return str_t[:-2]
    else:
        return str(int(h) + 12) + ":" + m


def read_raw_schedule(
    file_path: str
) -> pd.DataFrame:
    if not file_path.is_file():
        raise FileNotFoundError("schedule file not found!")

    raw_schedule = pd.read_csv(file_path)
    print(raw_schedule)
    print(0)


def write_itinerary():
    pass


def generate_itinerary():
    print(0)


def test():
    wd = Path(__file__).parents[1].absolute()
    schedule_file = wd.joinpath('data', 'profiles', 'sample_schedule.raw.csv')

    read_raw_schedule(file_path=schedule_file)

    # Driver Code         
    print(convert24("08:05am"))


if __name__ == "__main__":
    test()
    print(0)
