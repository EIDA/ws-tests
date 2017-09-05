#!/bin/bash

# run EIDA node performance test and create graph of results

PROFILE=/home/pikett/.profile
USERMAIL=fabian@sed.ethz.ch
DEPLOYDIR=/home/pikett/eida/ws-tests/eidanodetest/bin
DATADIR=/home/pikett/eida/data/eidanodetest/data
PLOTDIR=/home/pikett/eida/data/eidanodetest/plot

. ${PROFILE}

python ${DEPLOYDIR}/eida_test_single_node_request.py --responsesize=large \
	--excludenodes=iris,ncedc,usp \
	--services=post,arclink,federator --email=${USERMAIL} \
	--itersmall=6 \
	--od=${DATADIR}

sleep 5;

# all data
python ${DEPLOYDIR}/plot_node_requests_over_time.py \
    --id=${DATADIR} \
    --od=${PLOTDIR} \
    --of=eida_node_performance_over_time_all.png \
    --backend=png

# data of last 60 days
python ${DEPLOYDIR}/plot_node_requests_over_time.py \
    --id=${DATADIR} \
    --od=${PLOTDIR} \
    --of=eida_node_performance_over_time_last_60_days.png \
    --daysbefore=60 \
    --backend=png --markers
