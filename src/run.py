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

# @file     run.py
# @author   Jian Yang
# @date     2020-07-21


"""
generate sumoconfig file, and execute sumo program
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
from trip_generator import (
    generate_trips
)


T = 3600
R = 100


def run():
    wd = Path(__file__).parents[1].absolute()
    schedule_file = wd.joinpath('data', 'profiles', 'notre_dame_schedule.raw.csv')
    net_file = wd.joinpath('data', 'map', 'notre_dame.net.xml')
    loc_dict_file = wd.joinpath('data', 'map', 'notre_dame_loc_dict.csv')
    trip_save_dir = wd.joinpath('data', 'trips')

    # extract and build map data
    # options = ["-p", "notre_dame", "-d", "data/map"]
    # get_osm(options)

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

    # call scheduler to format the schedule (from raw schedule or sample)
    

    # call PLACEHOLDER to get the type/mode pref (ROUTE DEVICE here??)

    # call trip_generator to get the trip definition
    # TODO: needs to update get_mode on mode distr
    generate_trips(
        itin_df=itin_df,
        stop_distr=stop_distr,
        net=net,
        stop2edges=stop2edges,
        save_dir="",
        prefix='notre_dame'
    )

    # call duarouter -c xxxx.duarcfg to compute route files for cars and bike

    # write sumo config file and run sumo

    # processing output
    print(0)

if __name__ == "__main__":
    run()
