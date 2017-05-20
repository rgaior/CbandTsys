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
parser.add_argument("fitmethod", type=int, nargs='?',default='0', help="0: fit with gauss + 2nd order poly  / 1: fit with gauss + constant" )
parser.add_argument("-list", type=str, help="list of good days")
parser.add_argument("--deltatheta", type=int, nargs='?',default='0', help="delta theta")
parser.add_argument("--deltaphi", type=int, nargs='?',default='0', help="delta phi")

args = parser.parse_args()
delt = args.deltatheta
delp = args.deltaphi
fitmethod = args.fitmethod
stname = args.stname

print ' delt = ' ,delt ,' and delp = ', delp 
stname = args.stname
stid = constant.GDstationidbyname[stname]
if args.list:
    listfile = args.list
    goodlistname = listfile
else:
    goodlistname = stname + '.txt'
[goodyear,goodday] = utils.getdaysfromlist(constant.listfolder + goodlistname)

a_tsys = np.array([])
a_errtsys = np.array([])

datafolder = constant.dataresultfolder
it = 0 
nrofdays = 20
if fitmethod ==0:
    resfolder = constant.resfolder2
if fitmethod ==1:
    resfolder = constant.resfolder
if fitmethod ==2:
    resfolder = constant.resfolder3


#figfit, axarr = plt.subplots(nrofdays, 1, figsize=(10,4*nrofdays), sharex=True)
#for y,d in zip(goodyear[:nrofdays],goodday[:nrofdays]):
for y,d in zip(goodyear,goodday):
    y = int(y)
    d = int(d)
#    print goodyear , ' ', goodday
#    print  str(int(y)) , '_' , str(int(d)) 
    datafilename = datafolder + '/' + str(stid) + '/data_' + str(int(y)) + '_' + str(int(d)) + '.pkl'
#    print datafilename
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
#    print 'day = ' , day
    an = analyse.Analyse(day,delt,delp,thedata)
    simparam = an.getsimparam()

    an.correctbaseline(goodlistname)
    signalwindow = 4
    if fitmethod== 0:
        [fithours, fittedradio] = an.fitdata(signalwindow)
    if fitmethod== 1:
        [fithours, fittedradio] = an.fitdata(signalwindow,1)
    if fitmethod== 2:
        [fithours, fittedradio] = an.fitdata(signalwindow)
    
#    print fithours, fittedradio
#    an.isgoodfit()
    an.goodfit = True
    #########################################
    ######## check fit of  simulation #######
#     fitsim = utils.expofunc0(thedata.timesim, simparam[0], simparam[1], simparam[2], simparam[3])
#     simfit,ax0  = plt.subplots(1)
#     ax0.plot(thedata.timesim,thedata.sim,'o')
#     ax0.plot(thedata.timesim,fitsim)
#     ax0.set_xlabel('hours')
#     ax0.set_ylabel('sun temperature [K]')

    ######################################
    ######## check data correction #######
#     plt.plot(thedata.timedata,an.cbaseline)
#     plt.plot(thedata.timedata,thedata.data)
    
    ######################################
    ######## check fit of the data #######
#    if an.goodfit :        
    if type(an.fitresult[0]) is not type(0.0):        
#        print ' inside  ', an.fitresult[0]
        an.computetsys()
        an.geterrorsonfit()
        #         a_tsys = np.append(a_tsys,an.tsys)
#         a_errtsys = np.append(a_errtsys,an.errortsys)
        hourarray = utils.gethourarray(an.datasim.timedata)        
        #         [hourforfit,radioforfit] = an.getdataforfit(signalwindow)
#         fitres = an.fitresult 
        
        resfilename = resfolder + '/res_' + stname + '_' +str(delt) + '_' + str(delp) + '_' + str(y) + '_' + str(d) + '.pkl'
        out = open(resfilename,'wb')
        
        if fitmethod <2:
            pickle.dump(an,out)
        else:
            an.datasim = None
            an.cbaseline = np.array([])
#            print 'pickle analyse'
            pickle.dump(an,out)
        #        pickle.dump(an.fitresult,out)
        out.close()
#         fig = plt.figure()
#         plt.plot(hourarray, an.cbaseline,'.')
#         plt.plot(fithours, fittedradio,'-',lw=2)

        #        axarr[it].plot(fithours, radioforfit)
#         axarr[it].plot(hourarray, an.cbaseline,'.')
#         axarr[it].plot(fithours, fittedradio,'-',lw=2)
        
    it +=1

    ## compute weighted mean and error                                                                                                    
# tant = 0
# sigmatsysall = a_tsys*a_errtsys
# print 'a_tsys = ' , a_tsys
# print 'sigmatsysall = ' , sigmatsysall
# oneoversigmasquare = 1/(sigmatsysall*sigmatsysall)
# xoversigmasquare = a_tsys*oneoversigmasquare
# wmean = np.sum(xoversigmasquare)/np.sum(oneoversigmasquare)
# errorwmean = np.sqrt(1/np.sum(oneoversigmasquare))
# tsys = wmean + tant
# print 'tsys = ' , tsys
    
    
    
plt.show()
