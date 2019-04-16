
"""
Runs partition on the input MS
"""
import sys
import os
import numpy as np
import re

import config_parser
from config_parser import validate_args as va
from cal_scripts import get_fields

def get_effective_bw(spw, chanwidth):
    """
    Given an SPW selection, calculates the effective bandwidth across all
    selection parameters
    """

    nsel = len(spw.split(','))

    eff_bw = 0
    for ind, subspw in enumerate(spw.split(',')):
        is_chan = False

        # Determine whether frequency or channel selection
        if 'hz' not in subspw.lower():
            is_chan = True
            fac = chanwidth
        else:
            if re.search("(?i)\d+mhz", subspw):
                fac = 1E6
            elif re.search("(?i)\d+ghz", subspw):
                fac = 1E9
            elif re.search("(?i)\d+hz", subspw):
                fac = 1
            else:
                raise ValueError("Units format not recognized. ",
                        "Try one of Hz, MHz, GHz (case insensitive)")


        # Remove any unit characters for easier parsing later on
        subspw = re.sub("(?i)[mghz]", "", subspw)

        for ind2, ss in enumerate(subspw.split(';')):
            nums = [float(nn) for nn in ss.split('~') if nn.isdigit()]
            if len(nums) > 1:
                nums = sorted(nums)
                eff_bw += (nums[1] - nums[0])*fac
            else:
                eff_bw += chanwidth

        if is_chan:
            eff_bw *= chanwidth

    return eff_bw


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

    # Effective bandwidth in Hz
    eff_bw = get_eff_bw(spw, chanwidth)

    maxfracband = 0.1
    maxspwbw = maxfracband * eff_bw
    nchan = int(np.round(maxspwbw/chanwidth))
    nspw = int(np.round(eff_bw/maxspwbw))

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

