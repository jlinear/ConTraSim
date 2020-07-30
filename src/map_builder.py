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

# @file     map_builder.py
# @author   Jian Yang
# @date     2020-06-01

"""
An all-in-one tool to extract and build OpenStreetMap for the preprocessing of ConTraG.
Functions created in this script are modified and simplified based on the osmGet.py and
osmBuild.py scripts from SUMO tools. Refer to $SUMO_HOME/tools for the original version.
If no options offered, the main program will extract and convert the map of Notre Dame,
Indiana, USA.

Functions below can be imported separately outside this script:
- get_osm(): download osm data by bounding box;
- build_osm(): use netconvert and polyconvert to build SUMO readable network.

Outputs:
- $PREFIX$_bbox.osm.xml: raw map data
- $PREFIX$.net.xml: sumo readable network file for road networks
- $PREFIX$.netccfg: re-usable config file that generates the .net.xml file
- $PREFIX$.poly.xml: sumo readable polygon file for buildings and other polygons
- $PREFIX$.polycfg: re-usable config file that generates the .poly.xml file
"""

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import logging
import base64
import subprocess

try:
    import httplib
    import urlparse
except ImportError:
    # python3
    import http.client as httplib
    import urllib.parse as urlparse

SUMO_HOME = os.environ.get("SUMO_HOME")
if SUMO_HOME is None:
    raise TypeError('sumo not installed or $SUMO_HOME not found!')
tools_path = os.path.join(SUMO_HOME, 'tools')
sys.path.insert(0, tools_path)
import sumolib  # noqa


# A full list of options @ https://sumo.dlr.de/docs/NETCONVERT.html
DEFAULT_BUILD_OPTS = (
    "--geometry.remove,--verbose,"  # processing & reporting
    + "--sidewalks.guess,--crossings.guess,"  # pedestrian
    # + "--bikelanes.guess"  # bicycles
    + "--tls.default-type,actuated,--tls.guess-signals,--tls.discard-simple,--tls.join,"  # noqa tls
    + "--ramps.guess,"  # ramp
    + "--junctions.join,--junctions.corner-detail,5,"  # junctions
    + "--output.original-names,--output.street-names"  # output
)

TYEPMAP_DIR = os.path.join(SUMO_HOME, "data", "typemap")
TYPEMAPS = {
    "net": os.path.join(TYEPMAP_DIR, "osmNetconvert.typ.xml"),
    "urban": os.path.join(TYEPMAP_DIR, "osmNetconvertUrbanDe.typ.xml"),
    "pedestrians": os.path.join(TYEPMAP_DIR, "osmNetconvertPedestrians.typ.xml"),
    "bicycles": os.path.join(TYEPMAP_DIR, "osmNetconvertBicycle.typ.xml"),
    "poly": os.path.join(TYEPMAP_DIR, "osmPolyconvert.typ.xml"),
}

logging.basicConfig(format='map_builder:%(levelname)s: %(message)s')

optParser = optparse.OptionParser()
# file processing options
optParser.add_option("--osm-files", help="path to osm map file(s)")
optParser.add_option("-p", "--prefix", help="used in file naming for map and network")
optParser.add_option(
    "-b", "--bbox",
    help="bounding box to retrieve in geo coordinates \"west,south,east,north\""
)
optParser.add_option(
    "-d", "--output_dir", default=os.getcwd(),
    help="optional output directory (must already exist)"
)
# type map & options for netconvert
optParser.add_option(
    "--netconvert-typemap", default=None,
    help="typemap files for netconverter (optional)"
)
optParser.add_option(
    "--netconvert-options",
    default=DEFAULT_BUILD_OPTS, help="comma-separated options for netconvert"
)
# other netconvert options
optParser.add_option(
    "--lefthand", default=None, help="for lefthanded networks"
)
# type map and options for polyconvert (optional)
optParser.add_option(
    "--polyconvert-typemap", default=None,
    help="typemap file for the extraction of colored areas (non-road)"
)
optParser.add_option(
    "--polyconvert-options", default="-v,--osm.keep-full-type",
    help="comma-separated options for polyconvert"
)


def read_compressed(conn, urlpath, query, filename):
    conn.request(
        "POST", "/" + urlpath, """
        <osm-script timeout="240" element-limit="1073741824">
        <union>
            %s
            <recurse type="node-relation" into="rels"/>
            <recurse type="node-way"/>
            <recurse type="way-relation"/>
        </union>
        <union>
            <item/>
            <recurse type="way-node"/>
        </union>
        <print mode="body"/>
        </osm-script>""" % query
    )
    response = conn.getresponse()
    print(response.status, response.reason)
    if response.status == 200:
        out = open(os.path.join(os.getcwd(), filename), "wb")
        out.write(response.read())
        out.close()


def get_osm(args=None):
    options, args = optParser.parse_args(args=args)
    if not options.bbox:
        west, south, east, north = -86.28, 41.68, -86.22, 41.72
        logging.warning(
            "No bounding box assigned, use the default(WSEN): " +
            "-86.28, 41.68, -86.22, 41.72"
        )
    else:
        west, south, east, north = [float(v) for v in options.bbox.split(',')]
        if south > north or west > east:  # TODO: more checking rules
            optParser.error("Invalid geocoordinates in bounding box.")

    if not options.prefix:
        logging.warning(
            "No prefix assigned, use the default: osm"
        )
        options.prefix = "osm"

    if options.output_dir:
        options.prefix = os.path.join(options.output_dir, options.prefix)

    url = urlparse.urlparse("https://www.overpass-api.de/api/interpreter")
    if os.environ.get("https_proxy") is not None:
        headers = {}
        proxy_url = urlparse.urlparse(os.environ.get("https_proxy"))
        if proxy_url.username and proxy_url.password:
            auth = '%s:%s' % (proxy_url.username, proxy_url.password)
            headers['Proxy-Authorization'] = 'Basic ' + base64.b64encode(auth)
        conn = httplib.HTTPSConnection(proxy_url.hostname, proxy_url.port)
        conn.set_tunnel(url.hostname, 443, headers)
    else:
        conn = httplib.HTTPSConnection(url.hostname, url.port)

    read_compressed(
        conn,
        url.path,
        '<bbox-query n="%s" s="%s" w="%s" e="%s"/>' % (north, south, west, east),
        options.prefix + "_bbox.osm.xml"
    )
    conn.close()


def getRelative(dirname, option):
    ld = len(dirname)
    if option[:ld] == dirname:
        return option[ld+1:]
    else:
        return option


def build_osm(args=None, bindir=None):
    (options, args) = optParser.parse_args(args=args)

    netconvert = sumolib.checkBinary('netconvert', bindir)
    polyconvert = sumolib.checkBinary('polyconvert', bindir)

    if not options.osm_files:
        optParser.error("No osm file specified, netconvert must have a map file.")
    if not options.prefix:
        logging.warning("No prefix assigned, use the same prefix as .osm.xml")
        options.prefix = os.path.basename(options.osm_files).replace('_bbox.osm.xml', '')  # noqa
    if not os.path.isdir(options.output_dir):
        optParser.error('output directory "%s" does not exist' % options.output_dir)
    if options.output_dir:
        options.prefix = os.path.join(options.output_dir, options.prefix)

    net_file = options.prefix + ".net.xml"
    net_cfg = options.prefix + ".netccfg"
    poly_file = options.prefix + ".poly.xml"
    poly_cfg = options.prefix + ".polycfg"

    # NETCONVERT
    netconvertOpts = [netconvert]
    netconvertOpts += [
        "--osm-files", options.osm_files,
        "--output-file", net_file,
        "--save-configuration", net_cfg
    ]
    if options.netconvert_typemap:
        netconvertOpts += ["--type-files", options.netconvert_typemap]
    else:
        typefiles = [
            TYPEMAPS["net"], TYPEMAPS["urban"],
            TYPEMAPS["pedestrians"], TYPEMAPS["bicycles"]
        ]
        netconvertOpts += ["--type-files", ','.join(typefiles)]
    if options.lefthand:
        netconvertOpts += ["--lefthand"]
    netconvertOpts += options.netconvert_options.split(',')
    netconvertOpts = [getRelative(options.output_dir, o) for o in netconvertOpts]
    print(netconvertOpts)
    subprocess.call(netconvertOpts, cwd=options.output_dir)
    subprocess.call([netconvert, "-c", net_cfg], cwd=os.getcwd())

    # POLYCONVERT
    polyconvertOpts = [polyconvert]
    polyconvertOpts += [
        "--osm-files", options.osm_files,
        "--output-file", poly_file,
        "--save-configuration", poly_cfg,
        "-n", net_file
    ]
    if options.polyconvert_typemap:
        polyconvertOpts += ["--type-file", options.polyconvert_typemap]
    else:
        typefiles = TYPEMAPS["poly"]
        polyconvertOpts += ["--type-file", typefiles]
    if options.polyconvert_options:
        polyconvertOpts += options.polyconvert_options.split(',')
    polyconvertOpts = [getRelative(options.output_dir, o) for o in polyconvertOpts]
    print(polyconvertOpts)
    subprocess.call(polyconvertOpts, cwd=options.output_dir)
    subprocess.call([polyconvert, "-c", poly_cfg], cwd=os.getcwd())


if __name__ == "__main__":
    # options = ["-p", "notre_dame", "-d", "data/map"]
    # get_osm(options)
    # options += ["--osm-files", "data/map/notre_dame_bbox.osm.xml"]
    # build_osm(options)
    get_osm()
    build_osm()
