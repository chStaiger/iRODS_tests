"""
    Usage:
    1) Cleaning testdata and folders
                python testIRODS.py -c
    2) Testing the connection to the iRODS server via port 1247 and all data ports
        Uses by default the iRODS defaultResc as destination resource
                python testIRODS.py -o [-r <irods resource>]
    3) Performnace testing (takes a long time --> use screen or tmux)
        Uses by default the iRODS defaultResc as destination resource
                python testIRODS.py -p [-r <irods resource>]
"""

from iRODStestFunctions import createTestData, createEnvJSON, performance, connectivity, cleanUp
import csv
import getopt
import sys
import os

RED     = "\033[31m"
GREEN   = "\033[92m"
BLUE    = "\033[34m"
DEFAULT = "\033[0m"

def testConnectivity(iresource):
    #create test data
    createTestData()
    #setup iRODS environment
    uname   = "c.staiger"
    host    = "geohealth.data.uu.nl"
    zone    = "nluu11p"
    createEnvJSON(uname, host, zone)
    #test connectivity: "irodsRescScaleout" or "irodsResc"
    result = connectivity(iresource)
    print result

def testPerformance(iresource, resFile):
    #create test data
    createTestData()
    #setup iRODS environment
    uname   = "c.staiger"
    host    = "geohealth.data.uu.nl"
    zone    = "nluu11p"
    createEnvJSON(uname, host, zone)

    if not os.path.isdir(os.path.dirname(resFile)):
        raise Exception("Path does not exist: " + os.path.dirname(resFile))

    #test performance: "irodsRescScaleout" or "irodsResc"
    result = performance(iresource)
    with open(resFile,"wb") as out:
        csv_out=csv.writer(out)
        csv_out.writerow(["date","iresource", "client", "iget/iput", "size", "time"])
        for row in data:
            csv_out.writerow(row)

def main():
    """
    Usage:
    1) Cleaning testdata and folders
                python testIRODS.py -c
    2) Testing the connection to the iRODS server via port 1247 and all data ports
        Uses by default the iRODS defaultResc as destination resource
                python testIRODS.py -o [-r <irods resource>]
    3) Performnace testing (takes a long time --> use screen or tmux)
        Uses by default the iRODS defaultResc as destination resource
        Writes results to /home/<user>/results.csv
                python testIRODS.py -p [-r <irods resource>] [-s <csv file>]
    """
    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hr:s:cpo", ["help"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)

    if args != []:
        print "for help use --help"
        sys.exit(2)
 
    clean       = False
    connect     = False
    perform     = False
    resource    = "defaultResc"
    out         = os.environ["HOME"]+"/results.csv"

    for o, a in opts:
        print o, a
        if o in ("-h", "--help"):
            print "Help"
            print __doc__
            sys.exit(0)
        elif o == "-c":
            clean = True
        elif o == "-p":
            perform = True
        elif o == "-o":
            connect = True
        elif o == "-r":
            resource = a
        elif o == "-s":
            out = a
        else:
            print "option unknown"
            sys.exit(2)

    if clean and not perform and not connect:
        print "Cleaning"
        cleanUp()
    elif perform and not clean and not connect:
        print "Performance testing on resource", resource
        print "Writing results to", 
        testPerformance(resource, out)
    elif connect and not clean and not perform:
        print "Connection test on resource", resource
        testConnectivity(resource)
    else:
        print "%sOption combination not supported. For help use --help%s"  %(RED, DEFAULT)

if __name__ == "__main__":
    main()
