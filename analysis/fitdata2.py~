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

args = parser.parse_args()
fitmethod = args.fitmethod
stname = args.stname

stname = args.stname
stid = constant.GDstationidbyname[stname]
if args.list:
    listfile = args.list
    goodlistname = listfile
else:
    goodlistname = 'newlist_' +  stname + '.txt'
[goodyear,goodday] = utils.getdaysfromlist(constant.listfolder + goodlistname)
print goodlistname
a_tsys = np.array([])
a_errtsys = np.array([])

datafolder = constant.datafolder
if fitmethod ==0:
    datafitfolder = constant.datafitfolder
if fitmethod ==1:
    datafitfolder = constant.datafitfolder2

a_chi2 = np.array([])
#thetas = [0]
#phis = [0]
thetas = range(-30,0,2)
#thetas = range(29,,2)
phis = range(-30,30,2)
for t in thetas:
    for p in phis:
        print 't = ' , t, ' p =  ', p
        for y,d in zip(goodyear,goodday):
#        for y,d in zip(goodyear,goodday):
            y = int(y)
            d = int(d)
            datafilename = datafolder + '/' + str(stid) + '/data_' + str(int(y)) + '_' + str(int(d)) + '.pkl'
#            print datafilename
            if os.path.isfile(datafilename):
                datafile = open(datafilename,'rb')
            else:
                continue
            thedata = pickle.load(datafile)    
            simfile = constant.simresultfolder + str(stid) + '/exptemp_' + stname + '_'+str(t) + '_' + str(p) + '_' + str(y) + '_' + str(d) + '.txt'
            [h,m,temp] = utils.readtempfile(simfile)
            sec = 3600*h + 60*m    
            hour = h*100 + m*(100./60.)
            thedata.sim = temp
            thedata.timesim = hour
            
            day = utils.doytodate(y,d)
            an = analyse.Analyse(day,0,0,thedata)
            simparam = an.getsimparam()

            an.correctbaseline(stname)
            signalwindow = 4
            fitresult = an.fitdata2(signalwindow)
            [fithourarray,fitradio] = an.getdataforfit(4)
            if (fitresult.success == True):
#                 fig = plt.figure()
#                 plt.plot(fithourarray,fitradio)
#                 plt.plot(fithourarray, fitresult.best_fit, 'r-')
#                 plt.gca().text(np.mean(fithourarray),np.mean(fitradio), r'$\frac{\chi^2}{ndl} = $' +str(fitresult.redchi), fontsize=15)
#                saving part:
                outname = constant.datafit2folder + str(stid) + '/fit2_' + stname + '_' +str(t) + '_' + str(p) + '_' + str(y) + '_' + str(d) + '.txt'
                out = open(outname,'w')
                out.write(fitresult.fit_report())
                out.close()
                
                
plt.show()
