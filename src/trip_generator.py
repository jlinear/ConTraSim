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

# @file     trip_generator.py
# @author   Jian Yang
# @date     2020-07-21

"""
generate trip files from formatted itinerary for the given users.
TODO: expand it into large scale by using flow definitions
"""

import os, sys
import pandas as pd
import numpy as np
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")
import sumolib
from pathlib import Path
from typing import Dict
from get_taz import (
    read_loc_dict_file,
    get_stop_edges
)
from scheduler import (
    read_raw_schedule,
    generate_itinerary
)


R = 100
T = 3600


def read_intinerary(
    file_path: str
) -> pd.DataFrame:
    if not file_path.is_file():
        raise FileNotFoundError("itinerary file not found!")

    itin_df = pd.read_csv(file_path)
    return itin_df


def fill_null_stop(
    df: pd.DataFrame,
    stop_distr: pd.Series,
    eta: int = 2
) -> pd.DataFrame:
    """
    randomly choose corresponding number of stops from non-na stops and fillna
    """
    # T = df.index[1] - df.index[0]
    for idx, row in df.iterrows():
        if pd.isna(row['stop']):
            t = np.arange(np.mod(idx, 24*3600), 24*3600*5, 24*3600)
            t_range = np.concatenate([_t + np.arange(-eta*T, (eta+1)*T, T) for _t in t])
            t_range = t_range[(t_range >= 0) & (t_range < 24*3600*5)]
            stop_visited = df.loc[t_range]
            if stop_visited['stop'].notna().any():
                # fillna from non-na stops (Opt1: multiple stops fill in multi-na)
                non_na_stops = stop_visited[stop_visited['stop'].notna()]
                na_stops = stop_visited[stop_visited['stop'].isna()]
                stop_weights = non_na_stops['stop'].value_counts(normalize=True)
                len_na = na_stops.shape[0]
                fills = pd.Series(
                    np.random.choice(stop_weights.index, len_na, p=stop_weights),
                    index=na_stops.index
                )
                df['stop'].fillna(fills, inplace=True)
            else:
                # fillna from stop_distr
                fills = pd.Series(
                    np.random.choice(stop_distr.index, 1, p=stop_distr)[0],
                    index=stop_visited.index
                )
                # TODO： fill based on weighted prob or highest prob?
                df['stop'].fillna(fills, inplace=True)
    return df


def fill_null_stop_alt(
    df: pd.DataFrame,
    stop_distr: pd.Series,
    eta: int = 2
) -> pd.DataFrame:
    """
    randomly choose 1 stop from all non-na stops and fillna
    """
    # T = df.index[1] - df.index[0]
    for idx, row in df.iterrows():
        if pd.isna(row['stop']):
            t = np.arange(np.mod(idx, 24*3600), 24*3600*5, 24*3600)
            t_range = np.concatenate([_t + np.arange(-eta*T, (eta+1)*T, T) for _t in t])
            t_range = t_range[(t_range >= 0) & (t_range < 24*3600*5)]
            stop_visited = df.loc[t_range]
            if stop_visited['stop'].notna().any():
                # fillna from non-na stops (Opt1: multiple stops fill in multi-na)
                non_na_stops = stop_visited[stop_visited['stop'].notna()]
                na_stops = stop_visited[stop_visited['stop'].isna()]
                stop_weights = non_na_stops['stop'].value_counts(normalize=True)
                len_na = na_stops.shape[0]
                fills = pd.Series(
                    np.random.choice(stop_weights.index, 1, p=stop_weights)[0],
                    index=na_stops.index
                )
                df['stop'].fillna(fills, inplace=True)
            else:
                # fillna from stop_distr
                fills = pd.Series(
                    np.random.choice(stop_distr.index, 1, p=stop_distr)[0],
                    index=stop_visited.index
                )
                # TODO： fill based on weighted prob or highest prob?
                df['stop'].fillna(fills, inplace=True)
    return df


def generate_trips(
    itin_df: pd.DataFrame,
    stop_distr: Dict,
    net: sumolib.net,
    stop2edges: Dict,
    save_dir: str,
    prefix: str = 'sample'
) -> None:
    # open xml file, write header
    pt_path = save_dir.joinpath(prefix + "_persons.trips.xml")
    ct_path = save_dir.joinpath(prefix + "_cars.trips.xml")
    bt_path = save_dir.joinpath(prefix + "_bikes.trips.xml")
    pt_f = open(pt_path, "w")
    ct_f = open(ct_path, "w")
    bt_f = open(bt_path, "w")
    sumolib.xml.writeHeader(pt_f, script=None, root="routes", schemaPath="route_file.xsd")  # noqa
    sumolib.xml.writeHeader(ct_f, script=None, root="routes", schemaPath="route_file.xsd")  # noqa
    sumolib.xml.writeHeader(bt_f, script=None, root="routes", schemaPath="route_file.xsd")  # noqa

    for uid, itin in itin_df.groupby('uid'):
        itin = itin.drop(['uid', 'duration'], axis=1).set_index('timeslot')

        # fillna
        # 1) find the stops within 2T range same time of the week
        # if len(1) > 0: 2) keep stops within T/2 of driving distance and weighted select
        # else: 2) weighted select from stop_distr and apply to all five
        itin = fill_null_stop_alt(df=itin, stop_distr=stop_distr[uid], eta=2)
        print(uid)
        print(itin)

    # policy of whether to add a trip

    # policy of deciding mode of transport

    # choose depart based on randomness method, call a func here

    # choose from and to using stop2edges

    # write xml files

    # close files
    pt_f.write("</routes>\n")
    pt_f.close()
    ct_f.write("</routes>\n")
    ct_f.close()
    bt_f.write("</routes>\n")
    bt_f.close()
    pass


if __name__ == "__main__":
    wd = Path(__file__).parents[1].absolute()
    schedule_file = wd.joinpath('data', 'profiles', 'sample_schedule.raw.csv')
    net_file = wd.joinpath('data', 'map', 'notre_dame.net.xml')
    loc_dict_file = wd.joinpath('data', 'map', 'notre_dame_loc_dict.csv')
    trip_save_dir = wd.joinpath('data', 'trips')

    # get itinerary
    # itin_df = read_intinerary(file_path=itinerary_path)
    raw_sch = read_raw_schedule(file_path=schedule_file)
    itin_df, stop_distr = generate_itinerary(raw_sch=raw_sch, win_t=T)

    # read net
    net = sumolib.net.readNet(str(net_file))

    # read loc_dict
    loc_dict = read_loc_dict_file(file_path=loc_dict_file)

    # get stop to edges mapping
    stop2edges = get_stop_edges(net, loc_dict, R)

    # generate trips
    generate_trips(
        itin_df=itin_df,
        stop_distr=stop_distr,
        net=net,
        stop2edges=stop2edges,
        save_dir=trip_save_dir
    )

    print(0)
