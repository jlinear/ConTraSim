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

# @file     get_taz.py
# @author   Jian Yang
# @date     2020-07-01

MAX_NEIGHBOR = 8

import os, sys
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")
import sumolib
from typing import Tuple, List, TextIO
from pathlib import Path


class GeoPoint():
    def __init__(self, lat: float, lng: float):
        self.lat = lat
        self.lng = lng


class GeoPoly():
    def __init__(self, vertices: List[GeoPoint]):
        self.vertices = vertices


def get_nearby_edges(
    net: sumolib.net,
    center: GeoPoint,
    radius: float,
    max_neighbor: int = MAX_NEIGHBOR
) -> Tuple[List]:
    """
    get nearby edges for a given point
    """
    x, y = net.convertLonLat2XY(center.lng, center.lat)
    edges = net.getNeighboringEdges(x, y, radius)
    if len(edges) == 0:
        raise ValueError("no neighboring edges found, try an larger radius of ROI")
    ped_edges = [e for e in edges if e[0].allows('pedestrian')]
    car_edges = [e for e in edges if e[0].allows('passenger')]
    # TODO: add a return list for 'bicycle' edges, need to adjust net data first

    closest_ped_edges = sorted(ped_edges, key=lambda x: x[1])[:max_neighbor]
    closest_car_edges = sorted(car_edges, key=lambda x: x[1])[:max_neighbor]
    closest_ped_edges = list(list(zip(*closest_ped_edges))[0])
    closest_car_edges = list(list(zip(*closest_car_edges))[0])

    return closest_ped_edges, closest_car_edges


def get_nearby_edges_by_poly(
    net: sumolib.net,
    poly: GeoPoly,
    dist: float
) -> Tuple[List]:
    """
    get nearby edges of a given polygon
    """
    if len(poly.vertices) == 0:
        raise ValueError("not a valid polygon!")
    ped_edges = set()
    car_edges = set()
    for v in poly.vertices:
        p_e, c_e = get_nearby_edges(net, v, dist)
        ped_edges.update(p_e)
        car_edges.update(c_e)

    return ped_edges, car_edges


def write_taz_file(
    loc_dict_file: TextIO,
    net: sumolib.net,
    save_path: str,
    use_poly: bool = False
) -> None:
    """
    translate location dictionary into SUMO readable taz file
    """
    pass


if __name__ == "__main__":
    """
    The main is used for debugging only, all above funcs can be called directly
    The GeoPoint and polygon info/data come from location dictionary separately
    """
    wd = Path(__file__).parents[1].absolute()
    net_file = wd.joinpath('data', 'map', 'notre_dame.net.xml')
    loc_dict_file = wd.joinpath('data', 'map', 'loc_dict.csv')

    if not net_file.is_file():
        raise FileNotFoundError("not a valid network file")
    net = sumolib.net.readNet(net_file._str)


    p = GeoPoint(lat=41.702409, lng=-86.234141)
    r = 100
    edges1 = get_nearby_edges(net, p, r)
    # edges2 = get_nearby_edges_poly()
    print(0)
