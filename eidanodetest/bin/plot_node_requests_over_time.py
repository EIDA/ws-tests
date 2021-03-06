#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Plots results of web service tests from JSON result files over a 
timespan.

This file is part of the EIDA webservice performance tests.

"""

from __future__ import unicode_literals

import datetime
import dateutil
import glob
import importlib
import itertools
import os
import re
import sys

from gflags import DEFINE_boolean
from gflags import DEFINE_integer
from gflags import DEFINE_string
from gflags import FLAGS

import numpy

# avoid matplotlib X11 display problem when running headless
import matplotlib
matplotlib.use('Agg')

from matplotlib import rcParams
import matplotlib.patches as mpatches

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eidanodetest import utils



# only EIDA nodes
NODES = {
    'gfz': {
        'eida': True,
        'plot_order': 11,
        'legend_pos': 'ul'

        },
        
    'odc': {
        'eida': True,
        'plot_order': 10,
        'legend_pos': 'ul'
        },
        
    'eth': {
        'eida': True,
        'plot_order': 9,
        'legend_pos': 'ul'
        },
        
    'resif': {
        'eida': True,
        'plot_order': 8,
        'legend_pos': 'ul'
        },
        
    'ingv': {
        'eida': True,
        'plot_order': 7,
        'legend_pos': 'ul'
        },
        
    'bgr': {
        'name': 'BGR Hannover',
        'eida': True,
        'plot_order': 6,
        'legend_pos': 'ul'
        },
        
    'lmu': {
        'eida': True,
        'plot_order': 5,
        'legend_pos': 'ul'
        },
        
    'ipgp': {
        'eida': True,
        'plot_order': 4,
        'legend_pos': 'ul'
        },
        
    'niep': {
        'eida': True,
        'plot_order': 3,
        'legend_pos': 'ul'
        },
        
    'koeri': {
        'eida': True,
        'plot_order': 2,
        'legend_pos': 'ul'
        },
        
    'noa': {
        'eida': True,
        'plot_order': 1,
        'legend_pos': 'lr'
        }
}


COLORS = ('k', 'r', 'b', 'g', 'c', 'm')
SYMBOLS = (
    'o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X')

COL_IT = itertools.cycle(COLORS)
SYM_IT = itertools.cycle(SYMBOLS)


COMBINED_COLORS = ('k', 'r', 'b', 'm')    
COMBINED_SYMBOLS = ('o', '^', 'v', '<')

MARKERSIZE_THROUGHPUT = 3
MARKERSIZE_LATENCY = 2

LEGEND_ANCHOR_THROUGHPUT = (0.0, -2.0)
LEGEND_ANCHOR_LATENCY = (1.0, -2.0)

BIG_TITLE = "dataselect and arclink throughput/latency (~10 MiB response)"

PLOT_ABSCISSA = 'Days since {}'
PLOT_ORDINATE = 'Network throughput (Mbits / s)'
PLOT_ORDINATE_LATENCY = 'Latency (s)'

PLOT_MODELS_COLOR = '0.75'
PLOT_REFERENCE_COLOR = '0.0'
PLOT_REFERENCE_LINEWIDTH = 2

TITLE_FONTSIZE = 10
LEGEND_ALL_FONTSIZE = 6

PDF_BACKEND_DEFAULT = 'pdf'

PLOTSIZE_ONECOLUMN = (8, 8)
PLOTSIZE_TWOCOLUMNS = (7, 10)

# 1200 px
FIG_RESOLUTION_DPI = 150

PLOTS = {
    'dataselect-get': {
        'title': 'dataselect (GET) throughput',
        'filename': 'dataselect_get_throughput',
        'latency_color': 'g'
    },
    'dataselect-post': {
        'title': 'dataselect (POST) throughput',
        'filename': 'dataselect_post_throughput',
        'latency_color': 'c'
    },
    'dataselect-federator': {
        'title': 'federator dataselect throughput',
        'filename': 'federator_dataselect_throughput',
        'latency_color': 'y'
    },
    'arclink': {
        'title': 'ArcLink throughput',
        'filename': 'arclink_throughput'
    }
}


importlib.import_module('matplotlib.pyplot')
PYPLOT = sys.modules['matplotlib.pyplot']

SIZE_KEYS = ('small', 'medium', 'large', 'verylarge', 'huge')

SIZE_KEY = 'large'


DEFINE_string('backend', PDF_BACKEND_DEFAULT, 'Plot backend (default: pdf')
DEFINE_integer('daysafter', 0, 'Days after start date')
DEFINE_integer('daysbefore', 0, 'Days before end date')
DEFINE_string('enddate', '',  'End date')
DEFINE_string('id', '', 'Input directory')
DEFINE_string('od', '', 'Output directory')
DEFINE_string('of', '', 'Output file')
DEFINE_string(
    'requestsize', SIZE_KEY, 
    'Request size (small, medium, large, verylarge, huge)')
DEFINE_string('startdate', '', 'Start date')

DEFINE_boolean('markers', False, 'Line with markers')


def main():
    
    _ = FLAGS(sys.argv)
    
    if not FLAGS.id:
        error_msg = "you need to specify an input directory name with the "\
            "--id option"
        raise RuntimeError, error_msg

    # iterates through files with ascending time stamps
    # (earliest first)
    source_file_iterator = sorted(
        glob.iglob(
            os.path.join(FLAGS.id, utils.FILENAME_DATETIME_PATTERN_GLOB)))
    loop_file_count = len(source_file_iterator)
    
    first_timestamp = utils.get_timestamp_from_filename(
        source_file_iterator[0])
    last_timestamp = utils.get_timestamp_from_filename(
        source_file_iterator[-1])
    
    print "checking {} source files from {} until {}".format(
        loop_file_count, first_timestamp, last_timestamp)
    
    if FLAGS.startdate:
        if FLAGS.daysbefore > 0:
            error_msg = "--daysbefore is mutually exclusive with --startdate"
            raise RuntimeError, error_msg
        
        first_timestamp = dateutil.parser.parse(FLAGS.startdate)
        
    if FLAGS.enddate:
        if FLAGS.daysafter > 0:
            error_msg = "--daysafter is mutually exclusive with --enddate"
            raise RuntimeError, error_msg
        
        last_timestamp = dateutil.parser.parse(FLAGS.enddate)
    
    if FLAGS.daysbefore > 0:
        if FLAGS.daysafter > 0:
            error_msg = "--daysafter is mutually exclusive with --daysbefore"
            raise RuntimeError, error_msg
            
        first_timestamp = last_timestamp - datetime.timedelta(
            days=FLAGS.daysbefore)
        
    if FLAGS.daysafter > 0:
        if FLAGS.daysbefore > 0:
            error_msg = "--daysafter is mutually exclusive with --daysbefore"
            raise RuntimeError, error_msg
            
        last_timestamp = first_timestamp + datetime.timedelta(
            days=FLAGS.daysafter)
    
    if first_timestamp > last_timestamp:
        error_msg = "illegal time interval: start {}, end {}".format(
            first_timestamp, last_timestamp)
        raise RuntimeError, error_msg
    
    print "requested time interval: from {} until {}".format(
        first_timestamp, last_timestamp)
    
    data = {}
    timestamps = []
    
    for node in NODES:
        data[node] = dict()
            
        for plot_type in PLOTS:
            data[node][plot_type] = dict(ord=[], ord2=[])
                
    for file_idx, source_path in enumerate(source_file_iterator):
        
        # get datetime filename tail
        timestamp = utils.get_timestamp_from_filename(source_path)

        # check if timestamp in valid range
        if not utils.is_valid_timestamp(
                timestamp, first_timestamp, last_timestamp):
            continue
        
        try:
            d = utils.load_json(source_path)
        except Exception:
            print "WARNING: {} is not a valid (gzipped) JSON file".format(
                os.path.basename(source_path))
            continue
        
        timestamps.append(timestamp)
        last_filetail = utils.FILETAIL_DATETIME_PATTERN.search(
            source_path).group(1)
        
        for node, n_res in d.items():
                
            if node not in data:
                continue
        
            # dataselect-get, -post, or arclink
            for plot_type, plot_data in PLOTS.items():
            
                # http get, dataselect
                if plot_type == 'dataselect-get':
                    
                    try:
                        throughput = n_res['result'][SIZE_KEY]['http']\
                            ['dataselect']['get']['stats']['throughput'].get(
                                'median', numpy.nan)
                    except Exception:
                        throughput = numpy.nan
                         
                    try:
                        latency = n_res['result'][SIZE_KEY]['http']\
                            ['dataselect']['get']['stats']['latency'].get(
                                'median', numpy.nan)
                    except Exception:
                        latency = numpy.nan
               
                    data[node][plot_type]['ord'].append(throughput)
                    data[node][plot_type]['ord2'].append(latency)
                
                elif plot_type == 'dataselect-post':
                    
                    try:
                        throughput = n_res['result'][SIZE_KEY]['http']\
                            ['dataselect']['post']['stats']['throughput'].get(
                                'median', numpy.nan)
                    except Exception:
                        throughput = numpy.nan
                         
                    try:
                        latency = n_res['result'][SIZE_KEY]['http']\
                            ['dataselect']['post']['stats']['latency'].get(
                                'median', numpy.nan)
                    except Exception:
                        latency = numpy.nan
                    
                    data[node][plot_type]['ord'].append(throughput)
                    data[node][plot_type]['ord2'].append(latency)
                
                # only for EIDA nodes
                elif plot_type == 'dataselect-federator':
                    
                    try:
                        throughput = n_res['result'][SIZE_KEY]['http']\
                            ['dataselect']['federator']['stats']\
                                ['throughput'].get('median', numpy.nan)
                    except Exception:
                        throughput = numpy.nan
                         
                    try:
                        latency = n_res['result'][SIZE_KEY]['http']\
                            ['dataselect']['federator']['stats']['latency'].get(
                                'median', numpy.nan)
                    except Exception:
                        latency = numpy.nan
                    
                    data[node][plot_type]['ord'].append(throughput)
                    data[node][plot_type]['ord2'].append(latency)
                    
                # arclink, waveform
                elif plot_type == 'arclink':
                    
                    try:
                        throughput = n_res['result'][SIZE_KEY]['arclink']\
                            ['waveform']['stats']['throughput'].get(
                                'median', numpy.nan)
                    except Exception:
                        throughput = numpy.nan
                    
                    data[node][plot_type]['ord'].append(throughput)
    
    # abscissae
    abscissa_start = timestamps[0].date()
    abscissa_start_timestamp = datetime.datetime(
        abscissa_start.year, abscissa_start.month, abscissa_start.day, 0, 0, 
        0) - datetime.timedelta(days=1)
    days_since_beginning = []
    
    for ts in timestamps:
        timediff = ts - abscissa_start_timestamp
        frac_days = timediff.days + float(timediff.seconds) / (60 * 60 * 24)
        days_since_beginning.append(frac_days)
        
    print "using {} data points from {} until {}, abscissa starts at "\
        "{}".format(
            len(timestamps), timestamps[0], timestamps[-1], 
            abscissa_start_timestamp)
    
    if FLAGS.of:
        outfile = FLAGS.of
    else:
        outfile = "eida_nodes_over_time_{}.{}".format(
            last_filetail, FLAGS.backend.lower())
        
    outpath= utils.get_outpath(outfile, FLAGS.od)
    make_compare_plot_allnodes(
        outpath, abscissa_start_timestamp, days_since_beginning, data)


def make_compare_plot_allnodes(
    outpath, first_timestamp, days_since_beginning, data):
    
    print "plotting all node comparison"
    
    rcParams['figure.figsize'] = PLOTSIZE_ONECOLUMN
    
    col_count = 1
    row_count = 1 + len(data) / col_count
    
    figure = PYPLOT.figure()
    figure.clf()
    
    the_bigax = figure.add_subplot(111) 
    the_bigax2 = the_bigax.twinx()
    
    the_bigax.set_title(BIG_TITLE, fontdict={'size': TITLE_FONTSIZE})
    
    # Turn off axis lines and ticks of the big subplot
    for the_axis in (the_bigax, the_bigax2):
        the_axis.spines['top'].set_color('none')
        the_axis.spines['bottom'].set_color('none')
        the_axis.spines['left'].set_color('none')
        the_axis.spines['right'].set_color('none')
        the_axis.tick_params(
            labelcolor='w', top='off', bottom='off', left='off', right='off')
    
    the_bigax.set_xlabel(PLOT_ABSCISSA.format(first_timestamp))
    the_bigax.set_ylabel(PLOT_ORDINATE)
    the_bigax2.set_ylabel(PLOT_ORDINATE_LATENCY)
    
    for node in data:
        
        if node not in NODES:
            print "node {} unknown: not defined in plot script".format(node)
            continue
        
        print "plotting NODE: {}".format(node)
        plot_idx = NODES[node]['plot_order'] - 1
        n_res = data[node]
        
        row_idx = plot_idx / col_count
        
        if plot_idx % col_count == 0:
            col_idx = 0
        else:
            col_idx = 1
        
        the_ax = figure.add_subplot(row_count, col_count, plot_idx+1)
        the_ax2 = the_ax.twinx()
        
        for idx, plot_type in enumerate(PLOTS):
            
            #print "plot curve throughput: {}".format(plot_type)
            #print n_res[plot_type]['ord']
            
            if not(numpy.isnan(n_res[plot_type]['ord']).all()):
                
                if FLAGS.markers:
                    marker = COMBINED_SYMBOLS[idx]
                else:
                    marker = None
                  
                the_ax.plot(
                    days_since_beginning, n_res[plot_type]['ord'],                   
                    color=COMBINED_COLORS[idx], marker=marker,
                    markersize=MARKERSIZE_THROUGHPUT, label=plot_type)
                
            # http methods: latency
            if plot_type.startswith('dataselect') and not(
                numpy.isnan(n_res[plot_type]['ord2']).all()):
                    
                #print "plot curve latency: {}".format(plot_type)
                
                method = plot_type[len('dataselect-'):]
                label = "latency-{}".format(method)
                col = PLOTS[plot_type]['latency_color']
                
                if FLAGS.markers:
                    marker = 'o'
                else:
                    marker = None
                
                the_ax2.plot(
                    days_since_beginning, n_res[plot_type]['ord2'], 
                    color=col, marker=marker, linestyle='--', linewidth=1,
                    markersize=MARKERSIZE_LATENCY, label=label)
  
        ymin, ymax = the_ax.get_ylim()
        the_ax.set_ylim(0, 1.1 * ymax)
        
        xmin, xmax = the_ax.get_xlim()
        
        frac_x = 0.05 * (xmax - xmin)
        the_ax.set_xlim(xmin - frac_x, xmax + frac_x)
        
        ymin_2, ymax_2 = the_ax2.get_ylim()
        the_ax2.set_ylim(0, 1.1 * ymax_2)
        
        # axes label with node
        put_node_label(the_ax, node, xmin - frac_x, xmax, ymin, ymax)
        
        # legends (throughput and latency)
        # the selected axes must have all curves
        if plot_idx == len(data)-1: 
            
            the_ax2.legend(
                loc='lower right', bbox_to_anchor=LEGEND_ANCHOR_LATENCY, 
                fontsize=LEGEND_ALL_FONTSIZE)
            
            the_ax.legend(
                loc='lower left', bbox_to_anchor=LEGEND_ANCHOR_THROUGHPUT, 
                fontsize=LEGEND_ALL_FONTSIZE)
            
        else:
            
            the_ax.set_xticklabels([])
            the_ax2.set_xticklabels([])
    
    #figure.tight_layout()
    
    PYPLOT.savefig(
        outpath, format=FLAGS.backend.lower(), dpi=FIG_RESOLUTION_DPI)
    PYPLOT.close(figure)


def put_node_label(the_ax, node, xmin, xmax, ymin, ymax):

    # all y axes start at 0, so use ymin = 0
    ymin = 0

    the_ax.text(
        xmin, ymin, node, color='k', horizontalalignment='left', 
        verticalalignment='bottom')


if __name__ == '__main__':
    main()

