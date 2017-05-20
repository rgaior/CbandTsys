###########################################
## produce python type files             ##
## with radio, temp, humidity simulation ##
## out of the root file produced with    ##
## Corinne's code.                       ##
###########################################
import numpy as np
import sys
import os
cwd = os.getcwd()
classpath = cwd + '/../classes/'
utilspath = cwd + '/../utils/'
sys.path.append(utilspath)
sys.path.append(classpath)
import constant
import utils
import pickle
import dataset
import daydata
import argparse
import datetime

############################
##  argument parser       ##
############################
parser = argparse.ArgumentParser()
parser.add_argument("stname", type=str, nargs='?',default='popey', help="station name")

args = parser.parse_args()
stname = args.stname
stid = constant.GDstationidbyname[stname]
 
############################
## load the root file     ##
############################
filename = 'alldata.root'
file = constant.datafolder + 'GIGADuck/' +  filename

data = dataset.Dataset(file)
data.loaddata()
data = data.getnewdatawithid(stid)
data.selectleafs()

outfolder =  constant.dataresultfolder 
years = [2015,2016,2017] 
for y in years:
    for d in range(1,constant.doy[y]+1,1):
        sdatelim1 = utils.doytodate(y,d,hour=3)
        deltat = datetime.timedelta(1)
        sdatelim2 = sdatelim1 + deltat
        cond = np.where((data.date > sdatelim1) & (data.date < sdatelim2) )
        daydataset = data.getnewdatasetcond(cond)

        if (len(daydataset.date) == 0):
            continue
        ddata = daydata.Daydata('simpledata', y, d, daydataset.date, daydataset.radio, daydataset.tempLL, daydataset.humLL, [],[])

        #######################################
        ## save in pkl format the daily data ##
        #######################################
        outf = outfolder + str(stid)
        outfilename = outf + '/data_' + str(y) + '_' + str(d) + '.pkl'
        out = open(outfilename,'wb')
        pickle.dump(ddata,out)
        out.close()
