#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Runs small to huge FDSNWS and ArcLink requests to single nodes (EIDA and 
non-EIDA). Can be used for performance checking on a regular basis.

Records response time statistics in JSON file (TODO: database).

This file is part of the EIDA webservice performance tests.

Uses ObsPy ArcLink client.

"""

import datetime
import gzip
import io
import json
import os
import requests
import sys
import time

from gflags import DEFINE_integer
from gflags import DEFINE_string
from gflags import FLAGS

import numpy

from obspy import UTCDateTime
from obspy.clients.arclink.client import ArcLinkException
from obspy.clients.arclink.client import Client as ArclinkClient


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eidanodetest import settings
from eidanodetest import utils

DATETIME_TIMESTAMP_FORMAT_FOR_FILENAME_DATE = '%Y%m%d'
DATETIME_TIMESTAMP_FORMAT_FOR_FILENAME_SECOND = '%Y%m%d-%H%M%S'
DATETIME_TIMESTAMP_FORMAT_FOR_FILENAME_MICROSECOND = '%Y%m%d-%H%M%S-%f'


ALL_SERVERS = (settings.EIDA_NODES, settings.OTHER_SERVERS)

SERVICES_TO_TEST = ('get', 'post', 'federator', 'arclink')

TEST_SERVICES = {
    'http': {
        'methods':  ('get', 'post', 'federator'),
        'services': ('dataselect',)
        },
    'arclink': {
        'services': ('waveform',)
        }
}


# 10 minutes
TEST_TIME_INTERVAL_SMALL = 10 * 60

# 3 hours (180 minutes)
TEST_TIME_INTERVAL_MEDIUM = 3 * 60 * 60

# 12 hours (720 minutes)
TEST_TIME_INTERVAL_LARGE = 12 * 60 * 60

# 2 days (48 hours)
TEST_TIME_INTERVAL_VERYLARGE = 2 * 24 * 60 * 60

# 20 days
TEST_TIME_INTERVAL_HUGE = 20 * 24 * 60 * 60

ITERATION_COUNT_SMALL = 10
ITERATION_COUNT_LARGE = 5

TEST_TIME_INTERVALS = {
    'small': {
        'time_interval_duration': TEST_TIME_INTERVAL_SMALL,
        'iteration_count': ITERATION_COUNT_SMALL,
        'start': '2016-10-01T06:00:00', 'end': '2016-10-01T06:10:00'
        },
    'medium': {
        'time_interval_duration': TEST_TIME_INTERVAL_MEDIUM,
        'iteration_count': ITERATION_COUNT_SMALL,
        'start': '2016-10-01T06:00:00', 'end': '2016-10-01T09:00:00'
        },
    'large': {
        'time_interval_duration': TEST_TIME_INTERVAL_LARGE,
        'iteration_count': ITERATION_COUNT_SMALL,
        'start': '2016-10-01T06:00:00', 'end': '2016-10-01T18:00:00'
        },
    'verylarge': {
        'time_interval_duration': TEST_TIME_INTERVAL_VERYLARGE,
        'iteration_count': ITERATION_COUNT_LARGE,
        'start': '2016-10-01T06:00:00', 'end': '2016-10-03T06:00:00'
        },
    'huge': {
        'time_interval_duration': TEST_TIME_INTERVAL_HUGE,
        'iteration_count': ITERATION_COUNT_LARGE,
        'start': '2016-10-01T06:00:00', 'end': '2016-10-20T06:00:00'
        }
    }

OUTFILE_BASE = 'result_eida_nodetest'
OUTFILE_INDENT = 4
ARCLINK_USER_EMAIL = 'john.doe@example.com'


# --nodes list (default: all)
# --excludenodes (default: none)s
# --responsesize (small-huge, default: all)
# --services (get, post, federator, arclink)
# --of outfile
# --email (user e-mail, for ArcLink)
# --itersmall 10
# --iterlarge 5


DEFINE_string('nodes', '', 'Comma-separated list of nodes to be tested')
DEFINE_string(
    'excludenodes', '', 
    'Comma-separated list of nodes to be excluded from test')
DEFINE_string(
    'responsesize', '', 'Comma-separated list of response sizes to be tested:\
    small,medium,large,verylarge,huge')

DEFINE_string('services', '', 'Comma-separated list of services to be tested:\
    get,post,federator,arclink')
DEFINE_string('of', '', 'Output file')
DEFINE_string('od', '', 'Output directory')
DEFINE_string(
    'email', ARCLINK_USER_EMAIL, 
    'E-mail address of user running the test (for ArcLink)')

DEFINE_integer(
    'itersmall', ITERATION_COUNT_SMALL, 
    'Number of iterations for small, medium, and large response sizes')
DEFINE_integer(
    'iterlarge', ITERATION_COUNT_LARGE, 
    'Number of iterations for verylarge and huge response sizes')


def main():
    
    _ = FLAGS(sys.argv)
    
    global COMMANDLINE_PAR
    set_commandline_parameters()
    
    # init result dict
    result = init_result_dict()
    
    for time_int_category in COMMANDLINE_PAR['the_responsesize_list']:
        time_cat_info = TEST_TIME_INTERVALS[time_int_category]
        
        print "\n\n===== testing {} time intervals =====".format(
            time_int_category)
        
        # make iterations outer loop so that there is some time
        # between requests for the same node
        
        if time_int_category in ('verylarge', 'huge'):
            iteration_count = FLAGS.iterlarge
        else:
            iteration_count = FLAGS.itersmall
            
        for it in xrange(iteration_count):
            
            print "\n\n========== ITERATION {} of {} ==========".format(
                it + 1, iteration_count)
 
            # iterate over nodes
            for node, node_par in node_generator():
                
                payload = {
                    'network': node_par['testquerysncls']['network'],
                    'station': node_par['testquerysncls']['station'],
                    'location': node_par['testquerysncls']['location'],
                    'channel': node_par['testquerysncls']['channel'],
                    'starttime': TEST_TIME_INTERVALS\
                            [time_int_category]['start'],
                    'endtime': TEST_TIME_INTERVALS[time_int_category]\
                        ['end']
                }
                    
                # protocol (arclink, http fdsnws)
                for protocol, params in TEST_SERVICES.items():
                    
                    # skip arclink for huge request, no node
                    # delivers it
                    if protocol == 'arclink' and \
                        'arclink' in COMMANDLINE_PAR['the_services_list'] and \
                        'arclink' in node_par['services'] and \
                        'huge' != time_int_category:

                        # waveform, station, etc
                        for service in params['services']:
                                
                            print "\n\nquerying ARCLINK: %s" % (
                                node_par['services']['arclink']['server'])
                            
                            # check empty loc, wildcard *
                            # no comma-separated list allowed 
                            # in Arclink client
                            arclink_payload = convert_payload_to_arclink(
                                payload, node_par['testquerysncls'])

                            print arclink_payload
                                
                            # start timer
                            t_start = time.time()
                            
                            try:
                                client = ArclinkClient(
                                    host=node_par['services']['arclink']\
                                        ['server'],
                                    port=node_par['services']['arclink']\
                                        ['port'],
                                    user=FLAGS.email)
                                
                                with io.BytesIO() as bf:
                                    client.save_waveforms(
                                        bf,
                                        arclink_payload['network'], 
                                        arclink_payload['station'], 
                                        arclink_payload['location'], 
                                        arclink_payload['channel'], 
                                        UTCDateTime(
                                            arclink_payload['starttime']), 
                                        UTCDateTime(
                                            arclink_payload['endtime']),
                                        format='MSEED')
                                        
                                    length_bytes = len(bf.getvalue())
                                        
                            except Exception, e:
                                    
                                error_msg = "Arclink error: %s" % e
                                print error_msg
                                continue
                                
                            # time it
                            t_end = time.time()
                            t_req = t_end - t_start
                               
                            store_result(
                                result[node]['result'], length_bytes, 
                                t_req, arclink_payload, time_int_category, 
                                protocol, service)
                        
                    elif protocol == 'http':
                            
                        # dataselect, station
                        for service in params['services']:
                            
                            # GET, POST, federator (GET)
                            for method in params['methods']:
                                
                                # only requested methods/services
                                if method not in \
                                        COMMANDLINE_PAR['the_services_list']:
                                    continue
                                    
                                # service URL
                                if method == 'federator':
                                        
                                    # test federator only for EIDA nodes
                                    if node not in settings.EIDA_NODES:
                                        continue
                                    else:
                                        server = settings.EIDA_FEDERATOR_BASE_URL
                                else:
                                    server = node_par['services']['fdsn']\
                                        ['server']
                                    
                                endpoint = "%s/fdsnws/%s/1/query" % (
                                    server, service)
                                    
                                print "\n\nquerying HTTP {}: {}".format(
                                    method.upper(), endpoint)
                                
                                if method in ('get', 'federator'):
                                        
                                    # no cached version
                                    #headers = {
                                        #'cache-control': 'private, max-age=0, 
                                        #no-cache'}
                                        
                                    headers = {
                                        'cache-control': 'max-age=0,no-cache'}
                                        
                                    # start timer
                                    t_start = time.time()
                                        
                                    # fire GET request
                                    try:
                                        response = requests.get(
                                            endpoint, params=payload, 
                                            headers=headers, stream=False)
                                            
                                    except requests.exceptions.ConnectionError:
                                            
                                        error_msg = "error: no connection"
                                        print error_msg
                                        continue
                                        
                                    print "url: %s" % response.url
                                        
                                elif method == 'post':
                                        
                                    # POST params
                                    postdata = convert_payload_to_postdata(
                                        payload)
                                        
                                    print postdata
                                        
                                    # no cached version
                                    #headers = {
                                        #'cache-control': 'private, max-age=0, 
                                        #no-cache'}
                                        
                                    headers = {
                                        'cache-control': 'max-age=0,no-cache'}
                                        
                                    # start timer
                                    t_start = time.time()
                                        
                                    # fire POST request
                                    try:
                                        response = requests.post(
                                            endpoint, data=postdata, 
                                            headers=headers, stream=False)
                                            
                                    except requests.exceptions.ConnectionError:
                                            
                                        error_msg = "error: no connection"
                                        print error_msg
                                        continue
                                    
                                else:
                                    print "method {} not supported".format(
                                        method)
                                    continue
                                    
                                if not response.ok:
                                    error_msg = "service failed with "\
                                        "code %s" % (response.status_code)
                                    print error_msg
                                    continue

                                # time it
                                t_end = time.time()
                                t_req = t_end - t_start
                                    
                                content = response.content
                                length_bytes = len(content)
                                    
                                store_result(
                                    result[node]['result'], length_bytes, 
                                    t_req, payload, time_int_category, 
                                    protocol, service, method=method, 
                                    latency=response.elapsed.total_seconds())

    
    # compute stats
    for node, node_res in result.items():
        
        for time_int_category in COMMANDLINE_PAR['the_responsesize_list']:
            
            for protocol, params in TEST_SERVICES.items():
                
                for service in params['services']:
                    
                    base_loc = node_res['result'][time_int_category][protocol]\
                        [service]
                    
                    if protocol == 'arclink':
                        method_loop = ('arclink',)
                    else:
                        method_loop = TEST_SERVICES['http']['methods']
                    
                    for method in method_loop:
                        
                        if protocol == 'arclink':
                            stats_to = base_loc
                            write_to = base_loc['data']
                        else:
                            stats_to = base_loc[method]
                            write_to = base_loc[method]['data']
                        
                        if write_to['throughput']:
                    
                            print "\n----- {}: {}\n".format(
                                node, base_loc['params'])
                            
                            print "result size (MiB): %.3f" % (
                                base_loc['length'] / (1000.0 * 1000.0))
            
                            time_median = numpy.median(write_to['time'])
                            time_min = min(write_to['time'])
                            time_max = max(write_to['time'])
                            
                            tp_median = numpy.median(write_to['throughput'])
                            tp_min = min(write_to['throughput'])
                            tp_max = max(write_to['throughput'])
                            
                            print "t_req med/min/max (sec): %.3f %.3f %.3f" % (
                                time_median, time_min, time_max)
                            
                            print "Mbits_per_sec med/min/max: %.1f %.1f %.1f"\
                                % (tp_median, tp_min, tp_max)
                            
                            if write_to['latency']:
                                
                                la_median = numpy.median(write_to['latency'])
                                la_min = min(write_to['latency'])
                                la_max = max(write_to['latency'])
                                
                                print "latency med/min/max (sec): %.1f %.1f "\
                                    "%.1f" % (la_median, la_min, la_max)
                            
                                stats_to['stats'] = \
                                    dict(
                                        time=dict(
                                            median=time_median, min=time_min, 
                                            max=time_max),
                                        throughput=dict(
                                            median=tp_median, min=tp_min, 
                                            max=tp_max),
                                        latency=dict(
                                            median=la_median, min=la_min, 
                                            max=la_max))
                                        
                            else:
                                
                                stats_to['stats'] = \
                                    dict(
                                        time=dict(
                                            median=time_median, min=time_min, 
                                            max=time_max),
                                        throughput=dict(
                                            median=tp_median, min=tp_min, 
                                            max=tp_max))
    
    # write results to JSON file
    if FLAGS.of:
        outfile = FLAGS.of
    else:
        outfile = "{}_{}.json.gz".format(
            OUTFILE_BASE, 
            datetime.datetime.utcnow().strftime(
                DATETIME_TIMESTAMP_FORMAT_FOR_FILENAME_SECOND))
            
    outpath = utils.get_outpath(outfile, FLAGS.od)

    with gzip.open(outpath, 'wb') as fp:
        json.dump(result, fp, sort_keys=True, indent=OUTFILE_INDENT)


def init_result_dict():
    
    global COMMANDLINE_PAR
    
    result = dict()
    
    for node, node_par in node_generator():
        
        result[node] = dict()
        result[node]['result'] = dict()
        
        # reqsize/protocol/service/(method)/
        for sizemodel in COMMANDLINE_PAR['the_responsesize_list']:
            result[node]['result'][sizemodel] = dict()
            result[node]['result'][sizemodel]['http'] = dict()
            
            for service in ('dataselect',):
                
                result[node]['result'][sizemodel]['http'][service] = dict()
                
                for method in ('get', 'post', 'federator'):  
                    
                    result[node]['result'][sizemodel]['http'][service]\
                        [method] = dict()
                    result[node]['result'][sizemodel]['http'][service][method]\
                        ['data'] = dict()
            
                    init_result_store(
                        result[node]['result'][sizemodel]['http'][service]\
                            [method]['data'])

            result[node]['result'][sizemodel]['arclink'] = dict()
            
            for service in ('waveform',):
                result[node]['result'][sizemodel]['arclink'][service] = dict()
                result[node]['result'][sizemodel]['arclink'][service]['data'] \
                    = dict()
            
                init_result_store(
                    result[node]['result'][sizemodel]['arclink'][service]\
                        ['data'])
                
    return result


def init_result_store(result_dict):
            
    result_dict['length'] = []
    result_dict['time'] = []
    result_dict['throughput'] = []
    result_dict['latency'] = []
    

def convert_payload_to_arclink(payload, testsncls):
    
    pl = {}
    
    for key, value in payload.items():
        
        # if sncl contains comma-separated list, use only first entry
        if key in ('network', 'station', 'location', 'channel'):
            
            if ',' in testsncls[key]:
                s = testsncls[key].split(',')[0]
            else:
                s = testsncls[key]
                
            pl[key] = s.replace('?', '*')
            
        else:
            pl[key] = value
                                
    if pl['location'] == '--':
        pl['location'] = ''
        
    return pl
    

def convert_payload_to_postdata(payload):
    
    pl = ''
    
    sncl_arrays = {}
    for key in ('network', 'station', 'location', 'channel'):
    
        if ',' in payload[key]:
            sncl_arrays[key] = [x.strip() for x in payload[key].split(',')]
        else:
            sncl_arrays[key] = [payload[key],]
    
    starttime_str = UTCDateTime(payload['starttime']).datetime.isoformat()
    endtime_str = UTCDateTime(payload['endtime']).datetime.isoformat()
    
    for net in sncl_arrays['network']:
        for sta in sncl_arrays['station']:
            for loc in sncl_arrays['location']:
                for cha in sncl_arrays['channel']:
                    
                    pl += "{} {} {} {} {} {}\n".format(
                        net, sta, loc, cha, starttime_str, endtime_str)

        
    return pl


def get_node_par(node):
    
    node_par = None
    
    if node in settings.EIDA_NODES:
        node_par = settings.EIDA_NODES[node] 
    elif node in settings.OTHER_SERVERS:
        node_par = settings.OTHER_SERVERS[node]
    
    return node_par


def node_generator():
    
    global COMMANDLINE_PAR
    
    for node in COMMANDLINE_PAR['the_node_list']:
    
        node_par = get_node_par(node)
        
        if node not in COMMANDLINE_PAR['the_excludenode_list']:
            yield node, node_par


def store_result(
    result, length_bytes, t_req, payload, time_int_category, protocol, 
    service, method='', latency=None):
                        
    mbits_per_sec = 8 * length_bytes / (t_req * 1000 * 1000)
    print "%.3f MiB in %.2f seconds, %.2f Mbits/s" % (
        length_bytes / (1000.0 * 1000.0), t_req, mbits_per_sec)
                        
    result[time_int_category][protocol][service]['params'] = payload
    result[time_int_category][protocol][service]['length'] = length_bytes
                        
    # write to result list
    if protocol == 'http':
        write_to = result[time_int_category][protocol][service][method]['data']
    else:
        write_to = result[time_int_category][protocol][service]['data']

    write_to['length'].append(length_bytes)
    write_to['time'].append(t_req)
    write_to['throughput'].append(mbits_per_sec)
    
    if latency is not None:
        write_to['latency'].append(latency)


def set_commandline_parameters():
    
    if FLAGS.nodes:
        COMMANDLINE_PAR['the_node_list'] = [
            x.strip() for x in FLAGS.nodes.split(',')]
        
        for x in COMMANDLINE_PAR['the_node_list']:
            if not(x in settings.EIDA_NODES or x in settings.OTHER_SERVERS):
                raise ValueError, "node name {} unknown".format(x)
    else:
        
        COMMANDLINE_PAR['the_node_list'] = []
        for nodes in ALL_SERVERS:
            for node in nodes:
                COMMANDLINE_PAR['the_node_list'].append(node)
    
    # do not sanity-check excludenodes, just ignore them if they are unknown
    if FLAGS.excludenodes:
        COMMANDLINE_PAR['the_excludenode_list'] = [
            x.strip() for x in FLAGS.excludenodes.split(',')]
    else:
        COMMANDLINE_PAR['the_excludenode_list'] = []
    
    if FLAGS.responsesize:
        COMMANDLINE_PAR['the_responsesize_list'] = [
            x.strip() for x in FLAGS.responsesize.split(',')]
        
        for x in COMMANDLINE_PAR['the_responsesize_list']:
            if x not in TEST_TIME_INTERVALS:
                raise ValueError, "response size {} unknown".format(x)
                
    else:
        COMMANDLINE_PAR['the_responsesize_list'] = TEST_TIME_INTERVALS.keys()
    
    if FLAGS.services:
        COMMANDLINE_PAR['the_services_list'] = [
            x.strip() for x in FLAGS.services.split(',')]
        
        for x in COMMANDLINE_PAR['the_services_list']:
            if x not in SERVICES_TO_TEST:
                raise ValueError, "service {} unknown".format(x)
            
    else:
        COMMANDLINE_PAR['the_services_list'] = list(SERVICES_TO_TEST)
        
        
if __name__ == '__main__':
    COMMANDLINE_PAR = {}
    main()
