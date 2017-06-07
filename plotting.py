"""
Script to convert and plot the data collected  during the iRODS performance tests.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import os
import numpy

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

    #add new column to calculate gigabit/sec
    data['size GB'] = data['size']

    #reformat
    data['size GB'].replace(to_replace="[^0-9]+", value=r"", regex=True, inplace=True)
    data['size GB'] = pd.to_numeric(data['size GB'])

    idx = data['size GB'] == 10
    data['size GB'][idx] = 1
    idx = data['size GB'] == 100
    data['size GB'][idx] = 0.1

    data['size'].replace('10MB', '100x\n10MB', inplace=True)

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
            plt.ylabel('Gbit/s')
            plt.ylim([0, 9])
            plt.title(resc+' - iput from '+client)
            plt.savefig(resc+'-iput-'+client+'.png')

            data_mean   = dfIGET[idx].groupby('size').mean()
            data_mean.plot.bar()
            plt.xlabel('size')
            plt.ylabel('Gbit/s')
            plt.ylim([0, 5])
            plt.title(resc+' - iget from '+client)
            plt.savefig(resc+'-iget-'+client+'.png')

def plotDataCompute(dataFrame):
    """
    Creates separate grouped bar plots for the compute resources and the workstation results.
    Creates single figures for resource X [iput, iget].
    Shown is the mean performance per client.
    """
    plt.clf()

    dfIPUT = dataFrame[dataFrame['iget/iput']=='iput']
    dfIGET = dataFrame[dataFrame['iget/iput']=='iget']
    
    # make single plots for resources
    for resc in dataFrame['iresource'].unique():
        idx = (dataFrame['iresource']==resc)
        grouped = dfIPUT[idx].groupby(['size', 'client']).agg('mean') # calc of mean and store in column 'real time Gbit/s'
        groupedPUT = grouped.reset_index().pivot(index='size', columns='client', values='real time Gbit/s')

        grouped = dfIGET[idx].groupby(['size', 'client']).agg('mean')
        groupedGET = grouped.reset_index().pivot(index='size', columns='client', values='real time Gbit/s')

        # make grouped bar plots for lisa and cartesius
        groupedPUTComp = groupedPUT[['lisa', 'cartesius']]
        groupedGETComp = groupedGET[['lisa', 'cartesius']]
        
        groupedPUTComp.plot.bar()
        plt.xlabel('size')
        plt.ylabel('Gbit/s')
        plt.title(resc+' - iput')
        plt.ylim([0, 2])        
        plt.savefig(resc+'-iput-compute.png')
        
        groupedGETComp.plot.bar()
        plt.xlabel('size')
        plt.ylabel('Gbit/s')
        plt.title(resc+' - iput')
        plt.ylim([0, 2])
        plt.savefig(resc+'-iget-compute.png')

def plotDataWorkstation(dataFrame):
    plt.clf()

    dfIPUT = dataFrame[dataFrame['iget/iput']=='iput']
    dfIGET = dataFrame[dataFrame['iget/iput']=='iget']

    # make single plots for resources
    for resc in dataFrame['iresource'].unique():
        idx = (dataFrame['iresource']==resc)
        grouped = dfIPUT[idx].groupby(['size', 'client']).agg('mean') # calc of mean and store in column 'real time Gbit/s'
        groupedPUT = grouped.reset_index().pivot(index='size', columns='client', values='real time Gbit/s')

        grouped = dfIGET[idx].groupby(['size', 'client']).agg('mean')
        groupedGET = grouped.reset_index().pivot(index='size', columns='client', values='real time Gbit/s')

        # make barplots for workstation
        groupedPUTWork = groupedPUT['workstation']
        groupedGETWork = groupedGET['workstation']

        groupedPUTWork.plot.bar()
        plt.xlabel('size')
        plt.ylabel('Gbit/s')
        plt.title(resc+' - iput')
        plt.ylim([0, 2])
        plt.savefig(resc+'-iput-workstation.png')

        groupedGETWork.plot.bar()
        plt.xlabel('size')
        plt.ylabel('Gbit/s')
        plt.title(resc+' - iget')
        plt.ylim([0, 2])
        plt.savefig(resc+'-iget-workstation.png')


def plot():
    files = [f for f in os.listdir("../results/") if f.endswith('.csv')]
    dataFrame = readData(files)

    dataFrame['real time Gbit/s'] = dataFrame['size GB']*8/dataFrame['real time']
    #dataFrame['user time Gbit/s'] = dataFrame['size GB']*8/dataFrame['user time']
    #dataFrame['system time Gbit/s'] = dataFrame['size GB']*8/dataFrame['system time']
    
    plotDataCompute(dataFrame)
    plotDataWorkstation(dataFrame)
    
