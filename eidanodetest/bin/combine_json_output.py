#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Combines JSON result files for web service tests for different result sizes.

This file is part of the EIDA webservice performance tests.

"""

import json

SIZE_KEYS = ('small', 'medium', 'large', 'verylarge', 'huge')

INFILE_BASE = 'statistics_dataselect_'
OUTFILE = 'statistics_dataselect_small-huge.json'

outdict = {}

for size_key in SIZE_KEYS:
    
    infile = "%s%s.json" % (INFILE_BASE, size_key)
    
    with open(infile, 'r') as fh:   
        d = json.load(fh)
    
    if size_key == 'small':
        
        # copy first dict
        outdict.update(d)
    
    else:
        for node in d:
            outdict[node]['result'][size_key] = d[node]['result'][size_key]
     
    
with open(OUTFILE, 'w') as fout:
    json.dump(outdict, fout, sort_keys=True, indent=4)

