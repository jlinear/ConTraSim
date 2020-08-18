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

import datetime
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict


TIME_S = 0
TIME_E = 432000
T = 3600


def convert24(str_t: str) -> datetime.time:
    """
    convert 12h time string into 24h datetime.time format
    """
    tail = str_t[-2:]
    h, m = str_t[:-2].strip().split(':')

    if tail in ("AM", "am") and h == "12":
        ret = "00" + str_t[2:-2]
    elif tail in ("AM", "am"):
        if len(h) < 2:  # allows input as "1:30am"
            ret = "0" + str_t[:-2]
        else:
            ret = str_t[:-2]
    elif tail in ("PM", "pm") and str_t[:2] == "12":
        ret = str_t[:-2]
    else:
        ret = str(int(h) + 12) + ":" + m

    return datetime.datetime.strptime(ret, "%H:%M").time()


def to_seconds(row: pd.Series) -> pd.Series:
    """
    transform time into seconds on a weekly basis (Mon.-Fri.)
    """
    s = row["start_time"]
    e = row["end_time"]
    row["start_time"] = (s.hour * 60 + s.minute) * 60 + s.second + 24*3600*(row["day"]-1)  # noqa
    row["end_time"] = (e.hour * 60 + e.minute) * 60 + e.second + 24*3600*(row["day"]-1)

    return row[["uid", "start_time", "end_time", "location"]]


def find_closest(
    arr: np.array,
    v: float,
    side: str
) -> float:
    """
    given value v, find the closest element in a sorted array.
    left side: the closest x <= v
    right side: the closest x > v
    """
    left = 0
    right = len(arr) - 2
    while left < right:
        mid = left + (right - left) // 2
        if v - arr[mid] >= arr[mid + 2] - v:
            left = mid + 1
        else:
            right = mid

    if side == "left":
        return arr[left]
    elif side == "right":
        return arr[left+1]
    else:
        raise InterruptedError("Invalid param!")


def expand_to_slot(
    row: pd.Series,
    slots: np.array
) -> pd.DataFrame:
    """
    expand "start-end" based schedule to timeslot based schedule,
    with duration and stop info. attached
    """
    T = slots[1] - slots[0]
    df = pd.DataFrame(columns=["uid", "timeslot", "stop", "duration"])

    if row["s_left"] == row["e_left"]:
        df = df.append({
            "uid": row['uid'],
            "timeslot": row['s_left'],
            "stop": row['location'],
            "duration": row['end_time']-row['start_time']
        }, ignore_index=True)
    else:
        head_row = {
            "uid": row['uid'],
            "timeslot": row['s_left'],
            "stop": row['location'],
            "duration": row['s_right'] - row['start_time']
        }
        df = df.append(head_row, ignore_index=True)

        body_df = pd.DataFrame().assign(
            # uid=row['uid'],
            timeslot=np.arange(row['s_right'], row['e_left'], T),
            uid=row['uid'],
            stop=row['location'],
            duration=T
        )
        df = df.append(body_df, ignore_index=True)

        tail_row = {
            "uid": row['uid'],
            "timeslot": row['e_left'],
            "stop": row['location'],
            "duration": row['end_time'] - row['e_left']
        }
        df = df.append(tail_row, ignore_index=True)

    return df


def rm_itin_duplicates(
    df: pd.DataFrame,
    stop_distr: pd.Series
) -> pd.DataFrame:
    if df.shape[0] <= 1:
        ret_df = df
    else:
        dur_df = df.groupby(['uid','timeslot','stop']).sum()
        max_dur_df = dur_df.loc[dur_df.duration == dur_df.duration.max()].reset_index()
        if max_dur_df.shape[0] == 1:
            ret_df = max_dur_df
        else:
            stops = max_dur_df['stop']
            uid = max_dur_df.uid[0]
            stop_freq_df = pd.DataFrame(dict(freq=stop_distr[uid]), index=stops)
            ret_df = max_dur_df.loc[max_dur_df.stop == stop_freq_df.freq.idxmax()]
    return ret_df


def extract_schedule(
    sample_traj: str,
    th: float
) -> pd.DataFrame:
    pass


def read_raw_schedule(
    file_path: str
) -> pd.DataFrame:
    if not file_path.is_file():
        raise FileNotFoundError("schedule file not found!")

    raw_sch = pd.read_csv(file_path)
    raw_sch['start_time'] = raw_sch['start_time'].apply(convert24)
    raw_sch['end_time'] = raw_sch['end_time'].apply(convert24)

    raw_sch.sort_values(by=['uid', 'day', 'start_time', 'end_time'])

    return raw_sch


def write_itinerary(
    df: pd.DataFrame,
    save_path: str
) -> None:
    df.to_csv(save_path, index=False, na_rep="NULL")


def generate_itinerary(
    raw_sch: pd.DataFrame,
    win_t: int = T
) -> (pd.DataFrame, Dict):
    sch_in_sec = raw_sch.apply(to_seconds, axis=1)

    slots = np.arange(TIME_S, TIME_E, win_t)

    sch_in_sec["s_left"] = sch_in_sec["start_time"].apply(lambda x: find_closest(slots, x, "left"))  # noqa
    sch_in_sec["e_left"] = sch_in_sec["end_time"].apply(lambda x: find_closest(slots, x, "left"))  # noqa
    sch_in_sec["s_right"] = sch_in_sec["start_time"].apply(lambda x: find_closest(slots, x, "right"))  # noqa
    sch_in_sec["e_right"] = sch_in_sec["end_time"].apply(lambda x: find_closest(slots, x, "right"))  # noqa

    expand_to_slot(sch_in_sec.iloc[3], slots)
    sch_in_slot = pd.concat(
        [expand_to_slot(row, slots) for idx, row in sch_in_sec.iterrows()],
        axis=0
    )
    sch_in_slot.reset_index(inplace=True, drop=True)

    tmslt = pd.DataFrame(data=slots, columns=["timeslot"])
    uid = pd.DataFrame(data=sch_in_slot['uid'].unique(), columns=["uid"])
    tmslt['key'], uid['key'] = 1, 1
    uid_slot = pd.merge(uid, tmslt, on='key').drop("key", 1)

    itinerary = pd.merge(uid_slot, sch_in_slot, on=['uid', 'timeslot'], how='left')

    stop_distr = {}
    uid_group = itinerary.groupby(['uid'])
    for uid, df in uid_group:
        stop_distr[uid] = df['stop'].value_counts(normalize=True)

    itin_df = itinerary.groupby(['uid', 'timeslot']).apply(lambda x: rm_itin_duplicates(x, stop_distr))  # noqa
    itin_df.reset_index(drop=True, inplace=True)

    return itin_df, stop_distr


if __name__ == "__main__":
    wd = Path(__file__).parents[1].absolute()
    schedule_file = wd.joinpath('data', 'profiles', 'sample_schedule.raw.csv')
    itinerary_save_path = wd.joinpath('data', 'profiles', 'sample_itinerary.csv')

    raw_sch = read_raw_schedule(file_path=schedule_file)

    sch_in_slot = generate_itinerary(raw_sch=raw_sch)[0]
    write_itinerary(df=sch_in_slot, save_path=itinerary_save_path)
    # TODO: write stop_distr to file

    print(0)
