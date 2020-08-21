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


def run():
    # call map_buider to build the map

    # call scheduler to format the schedule (from raw schedule or sample)

    # call PLACEHOLDER to get the type/mode pref (ROUTE DEVICE here??)

    # call trip_generator to get the trip definition

    # call duarouter -c xxxx.duarcfg to compute route files for cars and bike

    # write sumo config file and run sumo

    # processing output
    pass


if __name__ == "__main__":
    pass
