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


def generate_trips(
    itin: pd.DataFrame,
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
    sumolib.xml.writeHeader(pt_f, script=None, root="routes", schemaPath="route_file.xsd")
    sumolib.xml.writeHeader(ct_f, script=None, root="routes", schemaPath="route_file.xsd")
    sumolib.xml.writeHeader(bt_f, script=None, root="routes", schemaPath="route_file.xsd")
    

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
        itin=itin_df,
        stop_distr=stop_distr,
        net=net,
        stop2edges=stop2edges,
        save_dir=trip_save_dir
    )

    print(0)
