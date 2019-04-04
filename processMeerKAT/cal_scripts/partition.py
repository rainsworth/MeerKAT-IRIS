
"""
Runs partition on the input MS
"""
import sys
import os
import numpy as np

import config_parser
from config_parser import validate_args as va
from cal_scripts import get_fields

def do_partition(visname, spw):
    # Get the .ms bit of the filename, case independent
    basename, ext = os.path.splitext(visname)
    filebase = os.path.split(basename)[1]

    mvis = filebase + '.mms'

    #mvis = os.path.split(visname.replace('.ms', '.mms'))[1]
    msmd.open(visname)
    nscan = msmd.nscans()
    # Get total BW and chan width for SPW 0
    # By default this should be the only SPW in MeerKAT data
    bandwidth = msmd.bandwidths(0)
    # Assume equal channel widths
    chanwidth = msmd.chanwidths(0)[0]
    msmd.close()
    msmd.done()

    maxfracband = 0.1 # Fractional bandwidth in percent
    maxspwbw = maxfracband * bandwidth
    nchan = int(np.round(maxspwbw/chanwidth))
    nspw = int(np.round(bandwidth/maxspwbw))

    mstransform(vis=visname, outputvis=mvis, createmms=True, separationaxis='scan',
            numsubms=nscan, spw=spw, datacolumn='DATA', regridms=True,
            width=nchan, nspw=nspw)

    #partition(vis=visname, outputvis=mvis, spw=spw, createmms=True, datacolumn='DATA',
    #        numsubms=nscan, separationaxis='scan')

    return mvis

def main():

    # Get the name of the config file
    args = config_parser.parse_args()

    # Parse config file
    taskvals, config = config_parser.parse_config(args['config'])

    visname = va(taskvals, 'data', 'vis', str)
    calcrefant = va(taskvals, 'crosscal', 'calcrefant', bool, default=False)
    refant = va(taskvals, 'crosscal', 'refant', str, default='m005')
    spw = va(taskvals, 'crosscal', 'spw', str, default='')

    mvis = do_partition(visname, spw)
    mvis = "'{0}'".format(mvis)
    vis = "'{0}'".format(visname)

    config_parser.overwrite_config(args['config'], conf_sec='data', conf_dict={'vis':mvis})
    config_parser.overwrite_config(args['config'], conf_sec='data', conf_dict={'orig_vis':vis})

if __name__ == '__main__':
    main()

