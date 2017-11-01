# -*- coding: utf-8 -*-
"""

This file is part of the EIDA webservice performance tests.

"""

import datetime
import gzip
import json
import os
import re

from mediator import settings

FILETAIL_DATETIME_PATTERN = re.compile(r'^.+(\d{8}-\d{6}).*$')

FILENAME_DATETIME_PATTERN = re.compile(
    r'^.+(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})(\d{2}).*$')
FILENAME_DATETIME_PATTERN_GLOB = '*[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-'\
    '[0-9][0-9][0-9][0-9][0-9][0-9]*'


EIDA_TEXT_COLOR_LINESTYLE = ('b', '-')
NON_EIDA_TEXT_COLOR_LINESTYLE = ('c', '--')
UNKNOWN_TEXT_COLOR_LINESTYLE = ('k', '..')


def load_json(source_path):

    # detect gzipped JSON by extension gz
    if source_path.endswith('gz'):
        
        with gzip.open(source_path, "rb") as fh:
            d = json.loads(fh.read().decode("utf-8"))
    else:
        
        with open(source_path, 'r') as fh:
            d = json.load(fh)
    
    return d


def get_outpath(outfile, dir=''):
    
    if dir:
        outpath = os.path.join(dir, outfile)
    else:
        outpath = outfile
    
    if os.path.dirname(outpath) and not(
        os.path.isdir(os.path.dirname(outpath))):
        
        os.makedirs(os.path.dirname(outpath))
        
    return outpath


def get_node_name(node):
    """Return node name"""
    
    name = node
    
    if node in settings.EIDA_NODES:
        name = settings.EIDA_NODES[node]['name']
    
    elif node in settings.OTHER_SERVERS:
        name = settings.OTHER_SERVERS[node]['name']
        
    return name


def get_node_text_color_linestyle(node):
    """color: EIDA blue, non-EIDA cyan, unknown black"""
    
    if node in settings.EIDA_NODES:
        color_ls = EIDA_TEXT_COLOR_LINESTYLE
        
    elif node in settings.OTHER_SERVERS:    
        color_ls = NON_EIDA_TEXT_COLOR_LINESTYLE
        
    else:
       color_ls = UNKNOWN_TEXT_COLOR_LINESTYLE

    return color_ls


def set_title(title, timestamp):
    
    if timestamp is not None:
        title = u'{}\n{}'.format(title, timestamp)
        
    return title


def get_timestamp_from_filename(path):
    
    timestamp = None
    
    # get datetime filename tail
    try:
        m = FILENAME_DATETIME_PATTERN.search(path)
        
        # tzinfo=timezones.UTC
        timestamp = datetime.datetime(
            year=int(m.group(1)),
            month=int(m.group(2)),
            day=int(m.group(3)),
            hour=int(m.group(4)),
            minute=int(m.group(5)),
            second=int(m.group(6)))
    
    except Exception:
        pass
    
    return timestamp


def is_valid_timestamp(timestamp, first, last):
    return (timestamp >= first and timestamp <= last)

