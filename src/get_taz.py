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
import csv
import logging
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")
import sumolib
from typing import Tuple, List, Dict, TextIO
from pathlib import Path

logging.basicConfig(format='get_taz:%(levelname)s: %(message)s')

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
    if len(closest_ped_edges) > 0:
        closest_ped_edges = list(list(zip(*closest_ped_edges))[0])
    if len(closest_car_edges) > 0:
        closest_car_edges = list(list(zip(*closest_car_edges))[0])

    return closest_ped_edges, closest_car_edges


def get_nearby_edges_by_poly(
    net: sumolib.net,
    poly: GeoPoly,
    radius: float
) -> Tuple[List]:
    """
    get nearby edges of a given polygon
    """
    if len(poly.vertices) == 0:
        raise ValueError("not a valid polygon!")
    ped_edges = set()
    car_edges = set()
    for v in poly.vertices:
        p_e, c_e = get_nearby_edges(net, v, radius)
        ped_edges.update(p_e)
        car_edges.update(c_e)

    return ped_edges, car_edges


def read_loc_dict_file(
    file_path: str,
    poly_based: bool = False
) -> Dict:
    if not file_path.is_file():
        raise FileNotFoundError("location dict file not found!")
    reader = csv.DictReader(open(file_path))

    loc_dict = {}
    for row in reader:
        if row['loc'] in loc_dict:
            raise ValueError('duplicate location value found: ' + row['loc'])
        if poly_based:
            pass  # TODO: parse poly vertices and store as GeoPoly
        else:
            loc_dict[row['loc']] = GeoPoint(float(row['lat']), float(row['lng']))

    return loc_dict


def generate_taz(
    loc_dict: Dict,
    net: sumolib.net,
    save_path: str,
    radius: float,
    use_poly: bool = False
) -> None:
    """
    translate location dictionary into SUMO readable taz file
    """
    fd = open(save_path, "w")
    sumolib.xml.writeHeader(fd, "$Id$", "tazs", "taz_file.xsd")
    if use_poly:
        # TODO: apply poly-based rules
        pass
    else:
        for loc in loc_dict:
            center = loc_dict[loc]
            p_e, c_e = get_nearby_edges(net, center, radius)
            # TODO: two different taz files for p_e and c_e
            if len(p_e + c_e) == 0:
                logging.warning("no edges found for taz: %s" % loc)
            all_edges = list(set(p_e+c_e))
            edge_ids = [x.getID() for x in all_edges]
            fd.write(
                '    <taz id="%s" edges="%s"/>\n' % (loc, ' '.join(edge_ids))
            )
    fd.write("</taz>\n")
    fd.close()


if __name__ == "__main__":
    """
    The main is used for debugging only, all above funcs can be called directly
    The GeoPoint and polygon info/data come from location dictionary separately
    """
    wd = Path(__file__).parents[1].absolute()
    net_file = wd.joinpath('data', 'map', 'notre_dame.net.xml')
    loc_dict_file = wd.joinpath('data', 'map', 'notre_dame_loc_dict.csv')

    if not net_file.is_file():
        raise FileNotFoundError("not a valid network file")
    net = sumolib.net.readNet(net_file._str)
    loc_dict_f = loc_dict_file
    loc_dict = read_loc_dict_file(file_path=loc_dict_file)

    save_path = wd.joinpath('data', 'map', 'notre_dame.taz.xml')
    generate_taz(loc_dict, net, save_path, 100)

    print(0)
