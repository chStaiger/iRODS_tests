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
    data = pd.concat(dataFrames)

    #reformat the columns real time, user time, system time: XmX.Xs --> X (in seconds)
    data['real time'] = data['real time'].apply(lambda x: 
        pd.to_numeric(x.split("m")[0])*60+pd.to_numeric(x.split("m")[1].strip('s')))
    data['user time'] = data['user time'].apply(lambda x:
        pd.to_numeric(x.split("m")[0])*60+pd.to_numeric(x.split("m")[1].strip('s')))
    data['system time'] = data['system time'].apply(lambda x:
        pd.to_numeric(x.split("m")[0])*60+pd.to_numeric(x.split("m")[1].strip('s')))

    #reformat the client column
    #cartesius workernodes start with 'tcn'
    tmp = ['cartesius' for i in data['client'] if i.startswith('tcn')]
    data['client'] = tmp

    return data


def plotData(dataFrame):

    # make single plots for iput and iget
    dfIPUT = dataFrame[dataFrame['iget/iput']=='iput']
    dfIGET = dataFrame[dataFrame['iget/iput']=='iget']
    
    fig, axes = plt.subplots(nrows=len(dataFrame['client'].unique()), ncols=len(dataFrame['iresource'].unique()), figsize=(6, 6), sharey=True)    
    stats = cbook.boxplot_stats(dfIPUT, labels=labels, bootstrap=10000)

    # make single plots for resources
    for resc in dataFrame['iresource'].unique():
        # make single plots for clients
        for client in dataFrame['client'].unique():
            # plot the times as boxplot
             


