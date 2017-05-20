###################################
## fit of the daily radio signal ##
###################################
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
cwd = os.getcwd()
classpath = cwd + '/../classes/'
utilspath = cwd + '/../utils/'
sys.path.append(utilspath)
sys.path.append(classpath)
from scipy.optimize import curve_fit
import datetime
import constant
import utils
import pickle
import dataset
import daydata
import analyse
import argparse
import matplotlib as mpl

############################
##  argument parser       ##
############################
parser = argparse.ArgumentParser()
parser.add_argument("stname", type=str, nargs='?',default='popey', help="station name")
parser.add_argument("--deltatheta", type=int, nargs='?',default='0', help="delta theta")
parser.add_argument("--deltaphi", type=int, nargs='?',default='0', help="delta phi")

args = parser.parse_args()
delt = args.deltatheta
delp = args.deltaphi
stname = args.stname

print ' delt = ' ,delt ,' and delp = ', delp 
stname = args.stname
stid = constant.GDstationidbyname[stname]
goodlistname = stname + '.txt'
[goodyear,goodday] = utils.getdaysfromlist(constant.listfolder + goodlistname)

a_tsys = np.array([])
a_errtsys = np.array([])

datafolder = constant.dataresultfolder
it = 0 
nrofdays = 20
#figfit, axarr = plt.subplots(nrofdays, 1, figsize=(10,4*nrofdays), sharex=True)
#for y,d in zip(goodyear[:nrofdays],goodday[:nrofdays]):
for y,d in zip(goodyear,goodday):
    y = int(y)
    d = int(d)
    datafilename = datafolder + '/' + str(stid) + '/data_' + str(int(y)) + '_' + str(int(d)) + '.pkl'
    print datafilename
    if os.path.isfile(datafilename):
        datafile = open(datafilename,'rb')
    else:
        continue
    thedata = pickle.load(datafile)    
    simfile = constant.simresultfolder + str(stid) + '/exptemp_' + stname + '_' +str(delt) + '_' + str(delp) + '_' + str(y) + '_' + str(d) + '.txt'
    [h,m,temp] = utils.readtempfile(simfile)
    sec = 3600*h + 60*m    
    hour = h*100 + m*(100./60.)
    thedata.sim = temp
    thedata.timesim = hour
    
    
    day = utils.doytodate(y,d)
    an = analyse.Analyse(day,delt,delp,thedata)
    simparam = an.getsimparam()


    #########################################
    ######## check fit of  simulation #######
#     fitsim = utils.expofunc0(thedata.timesim, simparam[0], simparam[1], simparam[2], simparam[3])
#    simfit,ax0  = plt.subplots(1)
    if np.max(thedata.sim) == 0:
        print ' hahahaha @'
    plt.plot(thedata.timesim,thedata.sim,'o')
#     ax0.plot(thedata.timesim,fitsim)
#     ax0.set_xlabel('hours')
#     ax0.set_ylabel('sun temperature [K]')

    ######################################
    ######## check data correction #######
#     plt.plot(thedata.timedata,an.cbaseline)
#     plt.plot(thedata.timedata,thedata.data)
    
    ######################################
    ######## check fit of the data #######
    
    
    
plt.show()
