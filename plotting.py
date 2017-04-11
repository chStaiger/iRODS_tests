"""
Script to convert and plot the data collected  during the iRODS performance tests.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook

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
    data = pd.concat(dataFrames, ignore_index=True)
    data.reset_index(inplace=True, drop=True)
    #reformat the columns real time, user time, system time: XmX.Xs --> X (in seconds)
    data['real time'] = data['real time'].apply(lambda x: 
        pd.to_numeric(x.split("m")[0])*60+pd.to_numeric(x.split("m")[1].strip('s')))
    data['user time'] = data['user time'].apply(lambda x:
        pd.to_numeric(x.split("m")[0])*60+pd.to_numeric(x.split("m")[1].strip('s')))
    data['system time'] = data['system time'].apply(lambda x:
        pd.to_numeric(x.split("m")[0])*60+pd.to_numeric(x.split("m")[1].strip('s')))

    #reformat the client column
    #cartesius workernodes start with 'tcn'
    for i in range(0, len(data['client'])):
        if data['client'][i].startswith('tcn'):
            data['client'][i] = 'cartesius'
        elif data['client'][i] == 'elitebook':
            data['client'][i] = 'workstation'

    return data


def plotData(dataFrame):

    # make single plots for iput and iget
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

files = ['singeFilePerfTest_cart0.csv', 'singeFilePerfTest_cart1_test.csv', 'singeFilePerfTest_cart2_test.csv', 'singeFilePerfTest_cart3_test.csv', 'results-1_rob.csv', 'results-2_rob.csv', 'results-3_rob.csv']

dataFrame = readData(files)
plotData(dataFrame)



