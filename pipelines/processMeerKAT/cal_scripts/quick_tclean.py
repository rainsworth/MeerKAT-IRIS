#Copyright (C) 2019 Inter-University Institute for Data Intensive Astronomy
#See processMeerKAT.py for license details.

import sys
import os

import config_parser
from config_parser import validate_args as va
from cal_scripts import bookkeeping
import glob

# CASA imports
from taskinit import *
from tasks import *
from casac import casac
msmd = casac.msmetadata()

def run_tclean(visname, fields, keepmms):
    """
    Run a quick and dirty tclean that will produce an image of the phase cal as well as the target.
    No W projection will be applied, and the image size and cell size are will be restricted to
    1024px and 1arcsec respectively, to keep the image creation reasonably quick.
    """

    #Store bandwidth in MHz
    msmd.open(visname)
    BW = msmd.bandwidths(-1)/1e6

    if keepmms == True:
        parallel = True
        extn = 'mms'
    else:
        parallel = False
        extn = 'ms'

    #Use 1 taylor term for BW < 100 MHz
    if BW < 100:
        terms = 1
        deconvolver = 'clark'
        suffix = ''
    else:
        terms = 2
        deconvolver = 'mtmfs'
        suffix = '.tt0'

    impath = os.path.join(os.getcwd(), 'images/')
    if not os.path.exists(impath):
        os.makedirs(impath)

    #Store target names
    targimname = []
    if len(fields.targetfield.split(',')) > 1:
        for tt in fields.targetfield.split(','):
            fname = msmd.namesforfields(int(tt))[0]
            tmpname = os.path.splitext(visname)[0] + '_%s.im' % (fname)
            targimname.append(os.path.join(impath, tmpname))
    else:
        fname = msmd.namesforfields(int(fields.targetfield))[0]
        tmpname = os.path.splitext(visname)[0] + '_%s.im' % (fname)
        targimname.append(os.path.join(impath, tmpname))

    #Image target and export to fits
    for ind, tt in enumerate(targimname):
        if len(targimname) > 1:
            field = fields.targetfield.split(',')[ind]
        else:
            field = fields.targetfield

        fname = msmd.namesforfields(int(field))[0]
        inname = '%s.%s.%s' % (os.path.splitext(visname)[0], fname, extn)

        if len(glob.glob(tt + '*')) == 0:
            tclean(vis=inname, imagename=tt, datacolumn='corrected',
                    imsize=[2048,2048], threshold=0, niter=1000,
                    weighting='briggs', robust=0, cell='2arcsec',
                    specmode='mfs', deconvolver=deconvolver, nterms=terms, scales=[],
                    savemodel='none', gridder='standard',
                    restoration=True, pblimit=0, parallel=parallel)

            exportfits(imagename=tt+'.image'+suffix, fitsimage=tt+'.fits')


    #Image all calibrator fields and export to fits
    for field in [fields.gainfields,fields.bpassfield]:
        for subf in field.split(','):
            fname = msmd.namesforfields(int(subf))[0]

            secimname = os.path.splitext(visname)[0]
            inname = '%s.%s.%s' % (secimname, fname, extn)
            secimname = os.path.join(impath, secimname + '_%s.im' % (fname))

            if len(glob.glob(secimname + '*')) == 0:
                tclean(vis=inname, imagename=secimname, datacolumn='corrected',
                        imsize=[512,512], threshold=0,niter=1000, weighting='briggs',
                        robust=0, cell='2arcsec', specmode='mfs', deconvolver=deconvolver,
                        nterms=terms, scales=[], savemodel='none', gridder='standard',
                        restoration=True, pblimit=0, parallel=parallel)

                exportfits(imagename=secimname+'.image'+suffix, fitsimage=secimname+'.fits')

    msmd.close()
    msmd.done()


if __name__ == '__main__':
    # Get the name of the config file
    args = config_parser.parse_args()

    # Parse config file
    taskvals, config = config_parser.parse_config(args['config'])

    visname = va(taskvals, 'data', 'vis', str)
    keepmms = va(taskvals, 'crosscal', 'keepmms', bool)

    fields = bookkeeping.get_field_ids(taskvals['fields'])

    run_tclean(visname, fields, keepmms)
