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

a_tsys = np.array([])
a_errtsys = np.array([])

datafolder = constant.datafolder
if fitmethod ==0:
    datafitfolder = constant.datafitfolder
if fitmethod ==1:
    datafitfolder = constant.datafitfolder2

a_chi2 = np.array([])
#for y,d in zip(goodyear[::10],goodday[::10]):
for y,d in zip(goodyear,goodday):
    y = int(y)
    d = int(d)
    datafilename = datafolder + '/' + str(stid) + '/data_' + str(int(y)) + '_' + str(int(d)) + '.pkl'
    if os.path.isfile(datafilename):
        datafile = open(datafilename,'rb')
    else:
        continue
    thedata = pickle.load(datafile)    
    simfile = constant.simresultfolder + str(stid) + '/exptemp_' + stname + '_0_0_' + str(y) + '_' + str(d) + '.txt'
    [h,m,temp] = utils.readtempfile(simfile)
    sec = 3600*h + 60*m    
    hour = h*100 + m*(100./60.)
    thedata.sim = temp
    thedata.timesim = hour
    
    day = utils.doytodate(y,d)
    print 'day = ' , day
    an = analyse.Analyse(day,0,0,thedata)
    simparam = an.getsimparam()

    an.correctbaseline(stname)
#    an.correctbaseline(goodlistname)
    signalwindow = 4
    if fitmethod== 0:
        [fithours, fittedradio] = an.fitdata(signalwindow)
    if fitmethod== 1:
        [fithours, fittedradio] = an.fitdata(signalwindow,1)
#    an.goodfit = True

    ######################################
    ######## check data correction #######
#    plt.plot(thedata.timedata,an.cbaseline)
#    plt.plot(thedata.timedata,thedata.data)
    [fithourarray,fitradio] = an.getdataforfit(4)
    an.pointuncert = an.geterroronpoint(signalwindow)
    chi2 = np.sum( ((fittedradio - fitradio)/(an.pointuncert) )**2)
#    print 'fittedradio - fitradio = ' ,fittedradio - fitradio
#    print 'chi2  = ' , chi2
#    print ' an.pointuncert = ' , an.pointuncert
    ndl = len(fittedradio) - 6 
#    print 'chi2/ndl  = ' , chi2/ndl
    a_chi2 = np.append(a_chi2,chi2/ndl)
    an.isgoodfit()

    if an.goodfit == False:
        print ' !!!!!!!!!!!!!!!!!!!!!!!!!!!'
        fig = plt.figure()
        plt.plot(fithours,fitradio)
        plt.plot(fithours,fittedradio,'r-',lw=2)
        plt.gca().text(np.mean(fithours),np.mean(fittedradio)-10, r'$\frac{\chi^2}{ndl} = $' +str(chi2/ndl), fontsize=15)
    elif chi2/ndl > 2:
        fig2 = plt.figure()
        plt.plot(fithours,fitradio)
        plt.plot(fithours,fittedradio,'g-',lw=2)
        plt.gca().text(np.mean(fithours),np.mean(fittedradio), r'$\frac{\chi^2}{ndl} = $' +str(chi2/ndl), fontsize=15)
    else:
        fig3 = plt.figure()
        plt.plot(fithours,fitradio)
        plt.plot(fithours,fittedradio,'c-',lw=2)
        plt.gca().text(np.mean(fithours),np.mean(fittedradio), r'$\frac{\chi^2}{ndl} = $' +str(chi2/ndl), fontsize=15)
#        plt.gca().text(np.mean(fithours),np.mean(fittedradio)-5, r'$\chi^2$ = ' +str(chi2/ndl), fontsize=15)
#        plt.gca().text(np.mean(fithours),np.mean(fittedradio)-10, r'rms = ' +str(an.pointuncert), fontsize=15)


#    if an.goodfit == False or chi2/ndl > 2:
#        continue
#    else:
#         resfilename = constant.datafitfolder + '/' + str(stid) +'/' + '/res_' + stname + '_0_0_' + str(y) + '_' + str(d) + '.pkl'
#         out = open(resfilename,'wb')
#     pickle.dump(an,out)
#     out.close()
#    it +=1
    
    
figchi2 = plt.figure()
figchi2.suptitle(stname)
plt.hist(a_chi2,bins=50)
plt.xlabel('chi 2')
plt.show()
