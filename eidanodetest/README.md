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

Resulting statistics on the test queries is written to a result 
gzipped JSON file (file is only written after all queries, so be sure to wait 
until all requests have been performed).

The script writes to a log file that is overwritten on every new run. Only
one instance of the script can run at the same time.

The full suite can be run as follows:

````
python eida_test_single_node_request.py --email=jane.doe@example.com
````

Please use your own e-mail address (this is only relevant for ArcLink 
requests).

**Command line options:**

  `--od`            Output directory (default: current directory).

  `--ld`            Log directory (default: current directory).
                    
  `--of`            Output filename (there is a default including date/time).
                    Should have the extension `.json.gz` in order to make plot
                    tool work. 

  `--nodes`         Comma-separated list of nodes
                    (gfz, odc, ethz, resif, ipgp, ingv, noa, koeri, niep, lmu, 
                    bgr, iris, ncedc, isp; default: all)
                    

  `--excludenodes`  Comma-separated list of nodes to be excluded (mutually
                    exclusive with --nodes)

  `--responsesize`  Comma-seperated list of target response sizes (small, 
                    medium, large, verylarge, huge; default: all)

  `--services`      Comma-separated list of services (get, post, arclink, 
                    federator; default: all)

  `--email`         E-mail address of querying person/institution

  `--itersmall`     Number of iterations for small, medium, large response size
                    (default: 10)

  `--iterlarge`     Number of iterations for verylarge and huge response size
                    (default: 5)

**Alternative servers:**

With the `--nodes` flag, you can specify non-standard servers for FDSNWS and
ArcLink per node, separated by `=` characters. The syntax is

````
--nodes="eth=http://eida2.ethz.ch=eida2.ethz.ch:18001"
````

Alternative servers for FDSNWS and ArcLink can be specified separately:

````
--nodes="eth=http://eida2.ethz.ch" (FDSNWS only)
--nodes="eth==eida2.ethz.ch:18001" (ArcLink only)
````

**Example call:**

````
python eida_test_single_node_request.py --responsesize=large \
    --excludenodes=iris,ncedc,usp \
    --services=post,arclink,federator --email=jane.doe@example.com \
    --itersmall=6 --od=/path/to/resultfiles \
    --ld=/path/to/logfile
````


Plotting of results for a single test run
-----------------------------------------

Creates a comparison plot of all methods (FDSNWS GET/POST, ArcLink, Federator)
per node, and comparison plots of node performance per method.

````
plot_single_node_requests.py --infile=/path/to/resultfile.json.gz
````

**Command line options:**

  `--infile`        Input file (required, .json or .json.gz).
  
  `--od`            Output directory (default: current directory).
  
  `--backend`       Plotting backend (from installed matplotlib backends,
                    default: pdf).

**Example call:**

````
python plot_single_node_requests.py \
    --infile=/path/to/resultfile.json.gz \
    --od=/path/to/plots \
    --backend=png
````


Plotting of results over time
-----------------------------

Result files are in `/path/to/resultfiles`, plots go to `/path/to/plots`.

````
plot_node_requests_over_time.py --id=/path/to/resultfiles
````

**Command line options:**

  `--id`            Input directory (required).
  
  `--od`            Output directory (default: current directory).
  
  `--of`            Output filename (should have proper extension for chosen
                    plotting backend).
  
  `--backend`       Plotting backend (from installed matplotlib backends,
                    default: pdf).
  
  `--daysafter`     Days to plot after starting date.
  
  `--daysbefore`    Days to plot before end date.
  
  `--startdate`     Plot data starting from this date (YYYY-MM-DD)
  
  `--enddate`       Plot data until this date (YYYY-MM-DD)
  
  `--requestsize`   Response size for which data is plotted (from: small, 
                    medium, large, verylarge, huge)
                    
  `--markers`       Show data markers in plot.


**Example call:**

````
python plot_node_requests_over_time.py \
    --id=/path/to/resultfiles \
    --od=/path/to/plots \
    --of=eida_node_performance_over_time_last_60_days.png \
    --daysbefore=60 \
    --backend=png --markers
````






