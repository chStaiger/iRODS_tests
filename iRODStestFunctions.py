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
    with open(testdata+"/sample100M.txt_0", "wb") as f:
        f.write(os.urandom(1024 * 1024 * 100))
    
    #1GB
    print "Write sample1G.txt"
    with open(testdata+"/sample1G.txt_0", "wb") as f:
        f.write(os.urandom(1024 * 1024 * 1024)) 
    
    #2GB
    print "Write sample2G.txt"
    with open(testdata+"/sample2G.txt_0", "wb") as f:
        f.write(os.urandom(1024 * 1024 * 1024 * 2))

    #5GB
    print "Write sample5G.txt"
    with open(testdata+"/sample5G.txt_0", "wb") as f:
        f.write(os.urandom(1024 * 1024 * 1024 * 5))

    #Folder of 100*10MB files
    print "Create 10MB*100"
    os.makedirs(testdata+"/Coll10MB_0")
    for i in range(100):
        with open(testdata+"/Coll10MB_0/sample10MB_"+str(i)+".txt", "wb") as f:
            f.write(os.urandom(1024 * 1024 * 10))

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
    p = subprocess.Popen(["time iput -r -K -f -R "+iresource+" "+source+" "+idestination],
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err = p.communicate()
    elapsed = [i.split("\t")[1] for i in err.strip("\n").split("\n")]
    return (out, err, elapsed[0], elapsed[1], elapsed[2])

def iRODSget(iresource, isource, destination):
    """
    Wrapper for iRODS iget.
    iresource:  iRODS resource name
    source:     path to local destination file, must be a file, accepts absolut and relative paths
    idestination:   iRODS source, accepts absolut and relative collection paths
    """
    p = subprocess.Popen(["time iget -r -K -f -R "+iresource+" "+isource+" "+destination],
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err = p.communicate()
    elapsed = [i.split("\t")[1] for i in err.strip("\n").split("\n")]
    return (out, err, elapsed[0], elapsed[1], elapsed[2])

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
        folders = [os.environ["HOME"]+"/testdata"]):
    """
    Removes iRODS collections and replicated testdata.
    collections:    List of absolut or relative collection names. Default ["CONNECTIVITY", "PERFORMANCE"].
    folders:        List of local folders. Default [os.environ["HOME"]+"/testdata"]
    """
    print "Remove iRODS collections"
    for coll in collections:
        p = subprocess.Popen(["irm -r "+coll],
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p = subprocess.Popen(["irmtrash"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    print "Remove duplicate data"
    data = []
    for folder in folders:
        data.extend([folder+"/" + f
            for f in os.listdir(folder) if not f.endswith("_0")])
    for d in data:
        if os.path.isfile(d):
            os.remove(d)
        else:
            os.rmdir(d)

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
    
def performanceSingleFiles(iresource, maxTimes = 10):
    """
    Tests the performance of iget and iput for single files.
    Test data needs to be stored under $HOME/testdata. The function omits subfolders. 
    It ping-pongs the data between the unix file system and iRODS collection:
        iput folder/data_0 --> coll/data_1
        iget coll/data_1 --> folder/data_1
        iput folder/data_1 --> coll/data_2
        iget coll/data_2 --> folder/data_2
        ...

    iresource:  iRODS resource
    maxTimes:   times how often the file is transferred with iput and iget.

    Returns a list of tuples: [(date, resource, client, iput/iget, size, real time, user time, system time)]
    """

    # Make sure you are in /home/<user>
    os.chdir(os.environ["HOME"])

    dataset = [os.environ["HOME"]+"/testdata/" + f 
        for f in os.listdir(os.environ["HOME"]+"/testdata") if os.path.isfile(os.environ["HOME"]+"/testdata/" + f)]
    for data in dataset:
        # Verify that data is there.
        if not os.path.isfile(data):
            print RED, "ERROR test data does not exist:", data, DEFAULT
            raise Exception("File not found.")

    print "Create iRODS Collection PERFORMANCE"
    collection = iRODScreateColl("PERFORMANCE")
    # Put and get data from iRODS using 1GB, 2GB and 5GB, store data with new file name "+_str(i)"
    result = []
    for data in dataset:
        data = data.split("_")[0] # ge base name of the file --> no "_str(i)"
        print "Put and get: ", data
        for i in tqdm(range(1, maxTimes)):
            date = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            print "iput", data+"_"+str(i-1), collection+"/"+os.path.basename(data)+"_"+str(i)
            out, err, real, user, sys = iRODSput(iresource, data+"_"+str(i-1), 
                collection+"/"+os.path.basename(data)+"_"+str(i))
            print "integrity", collection+"/"+os.path.basename(data+"_"+str(i)), data+"_"+str(i-1)
            if not checkIntegrity(collection+"/"+os.path.basename(data+"_"+str(i)), data+"_"+str(i-1)):
                print "%sERROR Checksums do not match.%s" %(RED, DEFAULT)
                raise Exception("iRODS Data integrity")
            else:
                print "Integrity done"
                result.append((date, iresource, os.uname()[1], "iput", os.path.basename(data).split('.')[0][6:], real, user, sys))
            
            date = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            print "iget", collection+"/"+os.path.basename(data)+"_"+str(i), data+"_"+str(i)
            out, err, real, user, sys = iRODSget(iresource, collection+"/"+os.path.basename(data+"_"+str(i)), 
                data+"_"+str(i))
            print "integrity", collection+"/"+os.path.basename(data+"_"+str(i)), data+"_"+str(i)
            if not checkIntegrity(collection+"/"+os.path.basename(data)+"_"+str(i), data+"_"+str(i)): 
                print "%sERROR Checksums do not match.%s" %(RED, DEFAULT)
                raise Exception("iRODS Data integrity")
            else:
                print "Integrity done"
                result.append((date, iresource, os.uname()[1], "iget", os.path.basename(data).split('.')[0][6:], real, user, sys))
    
    return result
