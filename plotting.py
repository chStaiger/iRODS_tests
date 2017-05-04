"""
Script to convert and plot the data collected  during the iRODS performance tests.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import os

# Read in a list of outputfiles
def readData(files):
    """
    files:  List of output files, formatted as csv
            Header:     date, resource, client, iput/iget, size, real time, user time, system time
    
    The columns '* time' are given in the format XmX.Xs. The function converts them to seconds.
    """

    #read data in
    dataFrames = []
    for csvFile in files:
        dataFrames.append(pd.read_csv(csvFile))

    #stack the dataframes
    data = pd.concat(dataFrames)
    data = data.reset_index(drop=True)

    #reformat the columns real time, user time, system time: XmX.Xs --> X (in seconds)
    data['real time'] = data['real time'].apply(lambda x: 
        pd.to_numeric(x.split("m")[0])*60+pd.to_numeric(x.split("m")[1].strip('s')))
    data['user time'] = data['user time'].apply(lambda x:
        pd.to_numeric(x.split("m")[0])*60+pd.to_numeric(x.split("m")[1].strip('s')))
    data['system time'] = data['system time'].apply(lambda x:
        pd.to_numeric(x.split("m")[0])*60+pd.to_numeric(x.split("m")[1].strip('s')))

    #reformat the client column
    #cartesius workernodes start with 'tcn'
    for c in data['client'].unique():
        if c.startswith('tcn'):
            data = data.replace(c, 'cartesius')
        elif 'lisa' in c:
            data = data.replace(c, 'lisa')
        elif c == 'elitebook':
            data = data.replace(c, 'workstation')


    return data


def plotData(dataFrame):

    dfIPUT = dataFrame[dataFrame['iget/iput']=='iput']
    dfIGET = dataFrame[dataFrame['iget/iput']=='iget']
    
    # make single plots for resources
    for resc in dataFrame['iresource'].unique():
        # make single plots for clients
        for client in dataFrame['client'].unique():
            # plot the times as boxplot
            idx = (dataFrame['iresource']==resc) & (dataFrame['client']==client)
            data_mean   = dfIPUT[idx].groupby('size').mean()
            data_mean.plot.bar()
            plt.xlabel('size')
            plt.ylabel('seconds')
            plt.title(resc+' - iput from '+client)
            plt.savefig(resc+'-iput-'+client+'.png')

            data_mean   = dfIGET[idx].groupby('size').mean()
            data_mean.plot.bar()
            plt.xlabel('size')
            plt.ylabel('seconds')
            plt.title(resc+' - iget from '+client)
            plt.savefig(resc+'-iget-'+client+'.png')

files = [f for f in os.listdir("../results/") if f.endswith('.csv')]
dataFrame = readData(files)
plotData(dataFrame)


