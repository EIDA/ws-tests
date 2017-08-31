#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Plots results of web service tests from JSON result files.

This file is part of the EIDA webservice performance tests.

"""

from __future__ import unicode_literals

import importlib
import itertools
import json
import os
import re
import sys

from gflags import DEFINE_string
from gflags import FLAGS

import numpy

import matplotlib
from matplotlib import rcParams
import matplotlib.patches as mpatches

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eidanodetest import settings

NODES = {
    'gfz': {
        'eida': True,
        'plot_order': 14,
        'legend_pos': 'ul'

        },
        
    'odc': {
        'eida': True,
        'plot_order': 13,
        'legend_pos': 'ul'
        },
        
    'eth': {
        'eida': True,
        'plot_order': 12,
        'legend_pos': 'ul'
        },
        
    'resif': {
        'eida': True,
        'plot_order': 11,
        'legend_pos': 'ul'
        },
        
    'ingv': {
        'eida': True,
        'plot_order': 10,
        'legend_pos': 'ul'
        },
        
    'bgr': {
        'name': 'BGR Hannover',
        'eida': True,
        'plot_order': 9,
        'legend_pos': 'ul'
        },
        
    'lmu': {
        'eida': True,
        'plot_order': 8,
        'legend_pos': 'ul'
        },
        
    'ipgp': {
        'eida': True,
        'plot_order': 7,
        'legend_pos': 'ul'
        },
        
    'niep': {
        'eida': True,
        'plot_order': 6,
        'legend_pos': 'ul'
        },
        
    'koeri': {
        'eida': True,
        'plot_order': 5,
        'legend_pos': 'ul'
        },
        
    'noa': {
        'eida': True,
        'plot_order': 4,
        'legend_pos': 'lr'
        },
    
    'iris': {
        'eida': False,
        'plot_order': 1,
        'legend_pos': 'lr'
    },
    
    # service.ncedc.org
    'ncedc': {
        'eida': False,
        'plot_order': 2,
        'legend_pos': 'lr'
    },

    'usp': {
        'eida': False,
        'plot_order': 3,
        'legend_pos': 'lr'
    }   
}


COLORS = ('k', 'r', 'b', 'g', 'c', 'm')
SYMBOLS = (
    'o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X')

COL_IT = itertools.cycle(COLORS)
SYM_IT = itertools.cycle(SYMBOLS)

EIDA_TEXT_COLOR_LINESTYLE = ('b', '-')
NON_EIDA_TEXT_COLOR_LINESTYLE = ('c', '--')
UNKNOWN_TEXT_COLOR_LINESTYLE = ('k', '..')


COMBINED_COLORS = ('k', 'r', 'b', 'm')    
COMBINED_SYMBOLS = ('o', '^', 'v', '<')

LEGEND_ANCHOR_THROUGHPUT = (-0.1, -1.5)
LEGEND_ANCHOR_LATENCY = (1.0, -1.5)

BIG_TITLE = "dataselect and arclink throughput/latency"

PLOT_ABSCISSA = 'Response size in Bytes'
PLOT_ORDINATE = 'Network throughput (Mbits / s)'
PLOT_ORDINATE_LATENCY = 'Latency (s)'

PLOT_MODELS_COLOR = '0.75'
PLOT_REFERENCE_COLOR = '0.0'
PLOT_REFERENCE_LINEWIDTH = 2

TITLE_FONTSIZE = 10
LEGEND_ALL_FONTSIZE = 6

PDF_BACKEND_DEFAULT = 'pdf'
PLOT_XSIZE = 10
PLOT_YSIZE = 10

#PLOT_BACKENDS = {
    #'pdf': {'extension': 'pdf'},
    #'png': {'extension': 'png'}
#}

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

 
#matplotlib.use(PDF_BACKEND)
importlib.import_module('matplotlib.pyplot')
PYPLOT = sys.modules['matplotlib.pyplot']

SIZE_KEYS = ('small', 'medium', 'large', 'verylarge', 'huge')
FILENAME_DATETIME_PATTERN = re.compile(r'^.+(\d{8}-\d{6})\.json$')


DEFINE_string('backend', PDF_BACKEND_DEFAULT, 'Plot backend (default: pdf')
DEFINE_string('infile', '', 'Input file')
DEFINE_string('od', '', 'Output directory')


def main():
    
    _ = FLAGS(sys.argv)
    
    if not FLAGS.infile:
        error_msg = "you need to specify an input file name with the "\
            "--infile option"
        raise RuntimeError, error_msg
    
    with open(FLAGS.infile, 'r') as fh:   
        d = json.load(fh)
    
    # get datetime filename tail
    m = FILENAME_DATETIME_PATTERN.search(FLAGS.infile)
    if m:    
        filetail = m.group(1)
    else:
        filetail = ''
    
    data = {}
    
    for node in d:
        data[node] = dict()
        
        for plot_type in PLOTS:
            data[node][plot_type] = dict(absc=[], ord=[], ord2=[])

    # dataselect-get, -post, or arclink
    for plot_type, plot_data in PLOTS.items():
        
        for node, n_res in d.items():
            
            for sk in SIZE_KEYS:
                    
                # http get, dataselect
                if plot_type == 'dataselect-get' and \
                    'length' in n_res['result'][sk]['http']['dataselect'] and \
                     'stats' in  n_res['result'][sk]['http']['dataselect']\
                         ['get']:
                    
                    #print n_res['result'][sk]['http']
                    
                    data[node][plot_type]['absc'].append(
                        n_res['result'][sk]['http']['dataselect']['length'])
                    data[node][plot_type]['ord'].append(
                        n_res['result'][sk]['http']['dataselect']['get']\
                            ['stats']['throughput']['median'])
                    data[node][plot_type]['ord2'].append(
                        n_res['result'][sk]['http']['dataselect']['get']\
                            ['stats']['latency']['median'])
                
                elif plot_type == 'dataselect-post' and \
                    'length' in n_res['result'][sk]['http']['dataselect'] and \
                     'stats' in  n_res['result'][sk]['http']['dataselect']\
                         ['post']:
                    
                    #print n_res['result'][sk]['http']
                    
                    data[node][plot_type]['absc'].append(
                        n_res['result'][sk]['http']['dataselect']['length'])
                    data[node][plot_type]['ord'].append(
                        n_res['result'][sk]['http']['dataselect']['post']\
                            ['stats']['throughput']['median'])
                    data[node][plot_type]['ord2'].append(
                        n_res['result'][sk]['http']['dataselect']['post']\
                            ['stats']['latency']['median'])
                
                # only for EIDA nodes
                elif plot_type == 'dataselect-federator' and \
                    'length' in n_res['result'][sk]['http']['dataselect'] and \
                     'stats' in  n_res['result'][sk]['http']['dataselect']\
                         ['federator']:
                    
                    #print n_res['result'][sk]['http']
                    
                    data[node][plot_type]['absc'].append(
                        n_res['result'][sk]['http']['dataselect']['length'])
                    data[node][plot_type]['ord'].append(
                        n_res['result'][sk]['http']['dataselect']['federator']\
                            ['stats']['throughput']['median'])
                    data[node][plot_type]['ord2'].append(
                        n_res['result'][sk]['http']['dataselect']['federator']\
                            ['stats']['latency']['median'])
                    
                # arclink, waveform
                elif plot_type == 'arclink' and \
                    'length' in n_res['result'][sk]['arclink']['waveform'] \
                        and 'stats' in \
                            n_res['result'][sk]['arclink']['waveform']:
                    
                    data[node][plot_type]['absc'].append(
                        n_res['result'][sk]['arclink']['waveform']['length'])
                    data[node][plot_type]['ord'].append(
                        n_res['result'][sk]['arclink']['waveform']['stats']\
                            ['throughput']['median'])
                   
        make_plot_allnodes(
            plot_data['filename'], data, plot_data['title'], plot_type, 
            filetail)
        
    for node, n_res in data.items():
        make_plot_node(
            "{}_{}_{}".format(node, 'http_arclink', filetail), n_res, node)
        
    make_compare_plot_allnodes("allnodes_compare_{}".format(filetail), data)


def make_compare_plot_allnodes(outfile, data):
    
    print "plotting all node comparison"
    
    rcParams['figure.figsize'] = (7, 10)
    
    col_count = 2
    row_count = 1 + len(data) / col_count
    
    figure = PYPLOT.figure()
    figure.clf()
    
    #figure.suptitle(BIG_TITLE, fontdict={'size': TITLE_FONTSIZE})
    
    the_bigax = figure.add_subplot(111) 
    the_bigax2 = the_bigax.twinx()
    
    the_bigax.set_title(BIG_TITLE, fontdict={'size': TITLE_FONTSIZE})
    
    # Turn off axis lines and ticks of the big subplot
    for the_ax in (the_bigax, the_bigax2):
        the_ax.spines['top'].set_color('none')
        the_ax.spines['bottom'].set_color('none')
        the_ax.spines['left'].set_color('none')
        the_ax.spines['right'].set_color('none')
        the_ax.tick_params(
            labelcolor='w', top='off', bottom='off', left='off', right='off')
    
    the_bigax.set_xlabel(PLOT_ABSCISSA)
    the_bigax.set_ylabel(PLOT_ORDINATE)
    the_bigax2.set_ylabel(PLOT_ORDINATE_LATENCY)
    
    for node in data:
        
        # no unicode
        #node = str(node)
        
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
            
            if n_res[plot_type]['absc'] and not all(
                numpy.array(n_res[plot_type]['ord']) <= 0):
                
                #print "plot curve throughput: {}".format(plot_type)
                the_ax.semilogx(
                    n_res[plot_type]['absc'], n_res[plot_type]['ord'],                   
                    color=COMBINED_COLORS[idx], marker=COMBINED_SYMBOLS[idx],
                    markersize=3, label=plot_type)
                
            # http methods: latency
            if plot_type.startswith('dataselect') and \
                n_res[plot_type]['absc'] and not all(
                    numpy.array(n_res[plot_type]['ord2']) <= 0):
                    
                #print "plot curve latency: {}".format(plot_type)
                
                method = plot_type[len('dataselect-'):]
                label = "latency-{}".format(method)
                col = PLOTS[plot_type]['latency_color']
                    
                the_ax2.semilogx(
                    n_res[plot_type]['absc'], n_res[plot_type]['ord2'], 
                    color=col, marker='o', linestyle='--', linewidth=1,
                    markersize=2, label=label)
            
        ymin, ymax = the_ax.get_ylim()
        the_ax.set_ylim(0, ymax)
        the_ax.set_xlim(1e5, 1.1e9)
        
        ymin_2, ymax_2 = the_ax2.get_ylim()
        the_ax2.set_ylim(0, ymax_2)
   
        # axes label with node
        put_node_label(the_ax, node, ymax, ymin)
        
        # legends (throughput and latency)
        # the selected axes must have all curves
        if plot_idx == len(data)-1: 
            the_ax.legend(
                loc='lower left', bbox_to_anchor=LEGEND_ANCHOR_THROUGHPUT, 
                fontsize=LEGEND_ALL_FONTSIZE)
            
        if plot_idx == len(data)-1: 
            the_ax2.legend(
                loc='lower right', bbox_to_anchor=LEGEND_ANCHOR_LATENCY, 
                fontsize=LEGEND_ALL_FONTSIZE)
    
    figure.tight_layout()
    
    filename = "{}.{}".format(outfile, FLAGS.backend.lower())
    outpath = get_outpath(filename)
    
    PYPLOT.savefig(outpath, format=FLAGS.backend.lower())
    PYPLOT.close(figure)


def make_plot_node(outfile, data, node):
    
    print "making all plots for node {}".format(node)
    
    rcParams['figure.figsize'] = (PLOT_XSIZE, PLOT_YSIZE)
    
    figure = PYPLOT.figure()
    figure.clf()
    
    the_ax = figure.add_subplot(1, 1, 1)
    
    figure.suptitle(
        "{} ({})".format(get_node_name(node), node.upper()), 
        fontdict={'size': TITLE_FONTSIZE})

    for idx, plot_type in enumerate(PLOTS):
        
        if data[plot_type]['absc'] and not all(
            numpy.array(data[plot_type]['ord']) <= 0):
        
            the_ax.semilogx(
                data[plot_type]['absc'], data[plot_type]['ord'], 
                color=COMBINED_COLORS[idx], marker=COMBINED_SYMBOLS[idx], 
                label=plot_type)

    ymin, ymax = the_ax.get_ylim()
    the_ax.set_ylim(0, ymax)
    
    the_ax.set_xlim(1e5, 1.1e9)
    
    the_ax.legend()
    
    the_ax.set_xlabel(PLOT_ABSCISSA)
    the_ax.set_ylabel(PLOT_ORDINATE)

    filename = "{}.{}".format(outfile, FLAGS.backend.lower())
    outpath = get_outpath(filename)
    
    PYPLOT.savefig(outpath, format=FLAGS.backend.lower())
    PYPLOT.close(figure)
    

def make_plot_allnodes(outfile, data, title, plot_type, filetail):
    
    print "plotting all nodes for {}".format(plot_type)
    
    rcParams['figure.figsize'] = (PLOT_XSIZE, PLOT_YSIZE)
    
    figure = PYPLOT.figure()
    figure.clf()
    
    the_ax = figure.add_subplot(1, 1, 1)
    figure.suptitle(title, fontdict={'size': TITLE_FONTSIZE})
    
    for node, n_res in data.items():

        col = COL_IT.next()
        sym = SYM_IT.next()
        
        if n_res[plot_type]['absc'] and n_res[plot_type]['ord'] and not all(
            numpy.array(n_res[plot_type]['ord']) <= 0):
            
            #print "node {}: {}".format(node, n_res[plot_type]['ord'])
            
            the_ax.semilogx(
                n_res[plot_type]['absc'], n_res[plot_type]['ord'], color=col, 
                linestyle=get_node_text_color_linestyle(node)[1], 
                marker=sym, label=node)
        
            # some have zero values at end
            for last_idx in reversed(xrange(len(n_res[plot_type]['ord']))):
                if n_res[plot_type]['ord'][last_idx] > 0.0:
                    the_ax.text(
                        1.1 * n_res[plot_type]['absc'][last_idx], 
                        n_res[plot_type]['ord'][last_idx], node, 
                        color=col)
                    break

    ymin, ymax = the_ax.get_ylim()
    the_ax.set_ylim(0, ymax)
    
    the_ax.set_xlim(1e5, 1.1e9)
    the_ax.legend()
    
    the_ax.set_xlabel(PLOT_ABSCISSA)
    the_ax.set_ylabel(PLOT_ORDINATE)

    filename = "{}_{}_{}.{}".format(
        outfile, plot_type, filetail, FLAGS.backend.lower())
    outpath = get_outpath(filename)
    
    PYPLOT.savefig(outpath, format=FLAGS.backend.lower())
    PYPLOT.close(figure)


def put_node_label(the_ax, node, ymax, ymin):

    # NOTE: do not put 0.0 as x coord, will raise an error (logarithmic)
    
    # all y axes start at 0, so use ymin = 0
    ymin = 0
    # lower right
    if NODES[node]['legend_pos'] == 'lr':
        the_ax.text(
            9.0e8, ymin + 0.05 * (ymax - ymin), node, 
            color=get_node_text_color_linestyle(node)[0], 
            horizontalalignment='right',verticalalignment='bottom')
    
    else:
        the_ax.text(
            1.5e5, 0.9 * ymax, node, 
            color=get_node_text_color_linestyle(node)[0], 
            horizontalalignment='left',verticalalignment='top')
        
        
def get_node_text_color_linestyle(node):
    """color: EIDA blue, non-EIDA cyan, unknown black"""
    
    if node in settings.EIDA_NODES:
        color_ls = EIDA_TEXT_COLOR_LINESTYLE
        
    elif node in settings.OTHER_SERVERS:    
        color_ls = NON_EIDA_TEXT_COLOR_LINESTYLE
        
    else:
       color_ls = UNKNOWN_TEXT_COLOR_LINESTYLE

    return color_ls
   

def get_node_name(node):
    """Return node name"""
    
    name = node
    
    if node in settings.EIDA_NODES:
        name = settings.EIDA_NODES[node]['name']
    
    elif node in settings.OTHER_SERVERS:
        name = settings.OTHER_SERVERS[node]['name']
        
    return name
        

def get_outpath(outfile):
    
    if FLAGS.od:
        outpath = os.path.join(FLAGS.od, outfile)
    else:
        outpath = outfile
        
    if not os.path.isdir(os.path.dirname(outpath)):
        os.makedirs(os.path.dirname(outpath))
        
    return outpath
        
    
if __name__ == '__main__':
    main()

