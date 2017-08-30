EIDA node performance tests
===========================

Single node response throughput/latency test
--------------------------------------------

This test evaluates throughput and latency for HTTP FDSNWS (dataselect) and 
ArcLink requests of different size. Currently, it is run against 11 EIDA nodes 
(as of August 2017), and, for comparison, against three nodes from North 
(IRIS, NCEDC) and South America (USP). Note that the code uses no parallel
threads/coroutines, so that every request uses the same, full network 
bandwidth, and no surge protection on the target nodes is triggered.
Running the whole suite of repeated access to all servers with five
different target response sizes takes several hours. It is possible to restrict
the number of tested servers, response sizes, iterations for each request, and
tested methods/services (fdsnws-dataselect GET/POST, ArcLink, EIDA Federator,
see description of command line parameters below).

Resulting statistics on the test queries is written to a result JSON file
(file is only written after all queries, so be sure to wait until all requests
have been performed).

The full suite can be run as follows:

````
python eida_test_single_node_request.py --email=fabian@sed.ethz.ch
````

Please use your own e-mail address (this is only relevant for ArcLink 
requests).

Command line options:

  --of            Output filename (there is a default including date/time). 

  --nodes         Comma-separated list of nodes
                  (gfz, odc, ethz, resif, ipgp, ingv, noa, koeri, niep, lmu, 
                  bgr, iris, ncedc, isp; default: all)

  --excludenodes  Comma-separated list of nodes to be excluded (mutually
                  exclusive with --nodes)

  --responsesize  Comma-seperated list of target response sizes (small, medium,
                  large, verylarge, huge; default: all)

  --services      Comma-separated list of services (get, post, arclink, 
                  federator; default: all)

  --email         E-mail address of querying person/institution

  --itersmall     Number of iterations for small, medium, large response size
                  (default: 10)

  --iterlarge     Number of iterations for verylarge and huge response size
                  (default: 5)
