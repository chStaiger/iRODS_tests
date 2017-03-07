# Author:   Christine Staiger
# Date:     March 1st 2017
# Version:  0.1

"""
Python functions to test the connectivity and performance of the iRODS icommands iput and iget.
"""

import os
import json
import subprocess
import time
from timeit import default_timer as timer
import hashlib
from tqdm import tqdm
import shutil


RED     = "\033[31m"
GREEN   = "\033[92m"
BLUE    = "\033[34m"
DEFAULT = "\033[0m"

def createTestData():
    """
    Creates test data. 
    Folder: /home/<usr>/testdata
    Files:  100MB, 1GB, 2GB, 5GB
    """
    
    testdata = os.environ["HOME"]+"/testdata"
    # Check whether test folder already exists. If not create one
    if os.path.isdir(testdata):
        print testdata, "exists"
    else:
        print "Create", testdata
        os.makedirs(testdata)

    # Create data
    #100MB
    print "Write sample100M.txt"
    with open(testdata+"/sample100M.txt", "wb") as f:
        f.truncate(1024 * 1024 * 100)
    
    #1GB
    print "Write sample1G.txt"
    with open(testdata+"/sample1G.txt", "wb") as f:
        f.truncate(1024 * 1024 * 1024)
    
    #2GB
    print "Write sample2G.txt"
    with open(testdata+"/sample2G.txt", "wb") as f:
        f.truncate(1024 * 1024 * 1024 * 2)
 
    #5GB
    print "Write sample5G.txt"
    with open(testdata+"/sample5G.txt", "wb") as f:
        f.truncate(1024 * 1024 * 1024 * 5)

    print "%sSUCCESS Test data created.%s" %(GREEN, DEFAULT)

def createEnvJSON(uname, host, zone, auth="PAM", ssl="none"):
    """
    Creates the irods_environment.json
    """

    # Check whether /home/<user>/.irods exists. If not create.
    irodsdir = os.environ["HOME"]+"/.irods"
    # Check whether test folder already exists. If not create one
    if os.path.isdir(irodsdir):
        print irodsdir, "exists"
    else:
        print "Create", irodsdir
        os.makedirs(irodsdir)

    # Create json file
    irodsDict = {}
    irodsDict["irods_user_name"]    = uname
    irodsDict["irods_host"]         = host
    irodsDict["irods_port"]         = 1247
    irodsDict["irods_zone_name"]    = zone
    irodsDict["irods_authentication_scheme"]    = auth
    irodsDict["irods_ssl_verify_server"]        = ssl

    print irodsDict

    # Write to disc
    print "Write", irodsdir+"/irods_environment.json"
    with open(irodsdir+"/irods_environment.json", "w") as f:
        json.dump(irodsDict, f)

    # Do an iinit to cache the password
    print "%sCaching password.%s" %(GREEN, DEFAULT) 
    subprocess.call(["iinit"], shell=True)
    subprocess.call(["ienv"], shell=True)
    print "%sSUCCESS iRODS environment setup.%s" %(GREEN, DEFAULT)

def iRODScreateColl(collname):
    """
    Creates an iRODS collection. If collection exists it starts 
    enumerating until new collection is created.
    collname:   Collection to create in iRODS, accepts absolute and relative collection paths
    """

    count = 0
    while(True):
        p = subprocess.Popen(["imkdir "+collname+str(count)], shell=True, 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if err.startswith("ERROR"):
            print RED, err, DEFAULT
            count = count + 1 
        else:
            break

    print GREEN, "SUCCESS iRODS collection created:", DEFAULT, collname+str(count)
    return collname+str(count)

def iRODSput(iresource, source, idestination):
    """
    Wrapper for iRODS iput.
    iresource:  iRODS resource name
    source:     path to local file to upload, must be a file, accepts absolut and relative paths
    idestination:   iRODS destination, accepts absolut and relative collection paths
    """
    start = timer()
    p = subprocess.Popen(["iput -K -f -R "+iresource+" "+source+" "+idestination],
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elapsed = timer() - start
    out, err = p.communicate()
    return (out, err, elapsed)

def iRODSget(iresource, isource, destination):
    """
    Wrapper for iRODS iput.
    iresource:  iRODS resource name
    source:     path to local destination file, must be a file, accepts absolut and relative paths
    idestination:   iRODS source, accepts absolut and relative collection paths
    """
    start = timer()
    p = subprocess.Popen(["iget -K -f -R "+iresource+" "+isource+" "+destination],
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elapsed = (timer() - start)
    out, err = p.communicate()
    return (out, err, elapsed)

def checkIntegrity(iRODSfile, localFile):
    """
    Compares checksums of local file and iRODS file. Uses md5.
    localFile:  absolut path to local file
    iRODSfile:  iRODS absolut or relative path
    """
    p = subprocess.Popen(["ils -L "+iRODSfile],
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    irodschksum = [item for item in out.split(" ") if item !=""][7]

    checksum = hashlib.md5(open(localFile, "rb").read()).hexdigest()

    return irodschksum == checksum

def cleanUp(collections = ["CONNECTIVITY0", "PERFORMANCE0"], 
        folders = [os.environ["HOME"]+"/testdata", os.environ["HOME"]+"/getdata"]):
    """
    Removes iRODS collections and testdata.
    collections:    List of absolut or relative collection names. Default ["CONNECTIVITY", "PERFORMANCE"].
    folders:        List of local folders. Default [os.environ["HOME"]+"/testdata"]
    """
    print "Remove iRODS collections"
    for coll in collections:
        p = subprocess.Popen(["irm -r "+coll],
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p = subprocess.Popen(["irmtrash"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    print "Remove folders"
    for folder in folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)    

    print "%sClean up finished. %s" %(GREEN, DEFAULT)

def connectivity(iresource, data=os.environ["HOME"]+"/testdata/sample100M.txt"):
    """
    Tests the conectivity to iresource with a 100MB file, checking port 1247 and the data ports.
    iresource:  iRODS resource
    homedir:    directory containing the testdata (home directory by default)    

    Returns a tuple: (date, resource, client, iput/iget, size, time)
    """
    # Make sure you are in /home/<user>
    os.chdir(os.environ["HOME"])
    # Verify that /home/<usr>/testdata/sample100M.txt is there.
    if not os.path.isfile(data):
        print "%sERROR test data does not exist: %s"+data %(RED, DEFAULT)
        raise Exception("File not found.")

    print "Create iRODS Collection CONNECTIVITY*"
    collection = iRODScreateColl("CONNECTIVITY")

    print "iput -f -K -R iresource", data, collection+"/sample100M.txt"    
    date = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    out, err, elapsed = iRODSput(iresource, data, collection+"/sample100M.txt")

    if err.startswith("ERROR"):
        print "%s" %(RED), err, "%s" %(DEFAULT)
        raise Exception("iRODS ERROR")

    # Test data integrity
    if not checkIntegrity(collection+"/sample100M.txt", data):
        print "%sERROR Checksums do not match.%s" %(RED, DEFAULT)
        raise Exception("iRODS Data integrity")

    result = (date, iresource, os.uname()[1], "iput", "100M", elapsed) 
    print GREEN, "SUCCESS", result, DEFAULT
    return (date, iresource, os.uname()[1], "iput", "100M", elapsed)
    
def performance(iresource):
    """
    Tests the performance of iget and iput.
    iresource: iRODS resource

    Returns a list of tuples: [(date, resource, client, iput/iget, size, time)]
    """

    # Make sure you are in /home/<user>
    os.chdir(os.environ["HOME"])

    # Create download folder for iget
    if not os.path.isdir(os.environ["HOME"]+"/getdata"):
        os.mkdir(os.environ["HOME"]+"/getdata") 
    destFolder = os.environ["HOME"]+"/getdata"

    dataset = [os.environ["HOME"]+"/testdata/" + f for f in os.listdir(os.environ["HOME"]+"/testdata")]
    for data in dataset:
        # Verify that data is there.
        if not os.path.isfile(data):
            print RED, "ERROR test data does not exist:", data, DEFAULT
            raise Exception("File not found.")

    print "Create iRODS Collection PERFORMANCE"
    collection = iRODScreateColl("PERFORMANCE")
    # Put and get data from iRODS using 1GB, 2GB and 5GB
    result = []
    for data in dataset:
        print "Put and get: ", data
        for i in tqdm(range(10)):
            date = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            out, err, elapsed = iRODSput(iresource, data, collection+"/"+os.path.basename(data))
            if not checkIntegrity(collection+"/"+os.path.basename(data), data):
                print "%sERROR Checksums do not match.%s" %(RED, DEFAULT)
                raise Exception("iRODS Data integrity")
            else:
                result.append((date, iresource, os.uname()[1], "iput", os.path.basename(data).split('.')[0][6:], elapsed))
            
            date = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            out, err, elapsed = iRODSget(iresource, collection+"/"+os.path.basename(data), 
                destFolder+"/"+os.path.basename(data))
            if not checkIntegrity(collection+"/"+os.path.basename(data), destFolder+"/"+os.path.basename(data)):
                print "%sERROR Checksums do not match.%s" %(RED, DEFAULT)
                raise Exception("iRODS Data integrity")
            else:
                result.append((date, iresource, os.uname()[1], "iget", os.path.basename(data).split('.')[0][6:], elapsed))
    
    return result
