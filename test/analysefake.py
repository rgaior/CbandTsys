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
parser.add_argument("-list", type=str, help="list of good days")
parser.add_argument("--deltatheta", type=int, nargs='?',default='0', help="delta theta")
parser.add_argument("--deltaphi", type=int, nargs='?',default='0', help="delta phi")

args = parser.parse_args()
delt = args.deltatheta
delp = args.deltaphi
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
a_hmax = np.array([])
a_simmax = np.array([])
a_max = np.array([])
a_simhmax = np.array([])
a_errtsys = np.array([])
a_errhmax = np.array([])
a_errmax = np.array([])
a_max = np.array([])
a_diffmax = np.array([])
datafolder = constant.dataresultfolder
it = 0 
nrofdays = 20
datearray = []
#figfit, axarr = plt.subplots(nrofdays, 1, figsize=(10,4*nrofdays), sharex=True)
#for y,d in zip(goodyear[:nrofdays],goodday[:nrofdays]):
for y,d in zip(goodyear,goodday):
    y = int(y)
    d = int(d)
    datafilename = datafolder + '/fake/' + str(stid) + '/data_' + str(int(y)) + '_' + str(int(d)) + '.pkl'
    print datafilename
    if os.path.isfile(datafilename):
        datafile = open(datafilename,'rb')
    else:
        continue
    thedata = pickle.load(datafile)    
    simfile = constant.simresultfolder + '/fake/' + '/exptemp_fake' + stname + '_' +str(delt) + '_' + str(delp) + '_' + str(y) + '_' + str(d) + '.txt'
    [h,m,temp] = utils.readtempfile(simfile)
    sec = 3600*h + 60*m    
    hour = h*100 + m*(100./60.)
    thedata.sim = temp
    thedata.timesim = hour
    
    day = utils.doytodate(y,d)
    an = analyse.Analyse(day,delt,delp,thedata)
    simparam = an.getsimparam()

    an.correctbaseline(goodlistname)
    signalwindow = 3 
    [fithours, fittedradio] = an.fitdata(signalwindow,1)

    an.isgoodfit()

    ######################################
    ######## check fit of the data #######
    if an.goodfit:
        print an.fitresult[0]
        an.computetsys()
        an.geterrorsonfit()
        datearray = np.append(datearray,an.day)
        a_tsys = np.append(a_tsys,an.tsys)
        a_errtsys = np.append(a_errtsys,an.errortsys)
        a_hmax = np.append(a_hmax,an.fitresult[0][2])
        a_simhmax = np.append(a_simhmax,an.simtofmax)
        a_simmax = np.append(a_simmax,an.simmax)
        a_errmax = np.append(a_errmax,np.sqrt(np.diag(an.fitresult[1]))[0])
        a_max = np.append(a_max,an.fitresult[0][0])
        a_diffmax = np.append(a_diffmax,an.fitresult[0][0] - utils.suntemptoadc(70, an.simmax))
        a_errhmax = np.append(a_errhmax,an.errortofmax)
        hourarray = utils.gethourarray(an.datasim.timedata)
#         fig = plt.figure()
#         plt.plot(hourarray, an.cbaseline,'.')
#         plt.plot(fithours, fittedradio,'-',lw=2)
    it +=1

print 'mean errror  = ', np.mean(a_errmax)
print 'mean diff  = ', np.mean(a_diffmax) , ' rms diff = ' , np.std(a_diffmax) 
#    compute weighted mean and error                                                                                                    
tant = 0
sigmatsysall = a_tsys*a_errtsys
print 'a_tsys = ' , a_tsys
print 'sigmatsysall = ' , sigmatsysall
oneoversigmasquare = 1/(sigmatsysall*sigmatsysall)
xoversigmasquare = a_tsys*oneoversigmasquare
wmean = np.sum(xoversigmasquare)/np.sum(oneoversigmasquare)
errorwmean = np.sqrt(1/np.sum(oneoversigmasquare))
tsys = wmean + tant
tsysall = a_tsys

print 'final result is ... Tsys = ' , tsys , ' +- ',  errorwmean
y = np.arange(0,len(tsysall),1)
x = np.arange(0,len(tsysall),1)
myticks = datearray
figres = plt.figure(figsize=(15,5))
figres.subplots_adjust(left=0.1, bottom=0.3, right=0.94, top=0.9,
                       wspace=None, hspace=None)
figres.suptitle(stname,fontsize=15,fontweight='bold')
#ax = plt.subplot(111)
theres = (tsys)*np.ones(len(y))
errtheres = errorwmean*np.ones(len(y))
ymin = np.min(tsysall-sigmatsysall)
ymax = np.max(tsysall+sigmatsysall)
#plt.errorbar(x,tsysall, yerr=sigmatsysall,lw=4, fmt='o',alpha=0.9,label='stat. and sys.')
plt.errorbar(x,tsysall, yerr=sigmatsysall,color='b', fmt='o',lw=4, alpha=0.6)
#plt.errorbar(x,tsysall, yerr=sigmatsysstat,color='b', fmt='o',lw=4, alpha=0.6,label='stat. only')

plt.xticks(x,myticks,rotation='vertical',size=10)
plt.fill_between(x, theres-errtheres, theres +  errtheres,facecolor='red',alpha=0.5)
plt.ylabel('system temperature [K]')
plt.ylim(ymin,ymax)
plt.legend()
#plt.xlim(35,185)
#plt.ylim(y[0]-0.5,y[-1]+0.5)
#textstr = '\n $T_{sys}=%.1f \pm%.1f [K]$'%(tsys, errorwmean)
textstr = '$T_{sys}=%.1f \pm%.1f [K]$'%(tsys, errorwmean)
#textstr = '$testo$'
props = dict(boxstyle='round', facecolor='white')
#plt.gca().text(0.95, 0.9, textstr, transform=plt.gca().transAxes, fontsize=17, fontweight ='bold', verticalalignment='top',horizontalalignment='right', bbox=props)
plt.gca().text(0.05, 0.9, textstr, transform=plt.gca().transAxes, fontsize=17, fontweight ='bold', verticalalignment='top',horizontalalignment='left', bbox=props)

#bins = np.linspace(0,300,150)
#plt.hist(tsysall,bins=bins)

fighmax = plt.figure(figsize=(15,5))
#figres.suptitle(stname,fontsize=15,fontweight='bold')
fighmax.subplots_adjust(left=0.1, bottom=0.3, right=0.94, top=0.9,
                       wspace=None, hspace=None)
plt.errorbar(x,(a_hmax-3)*100,yerr=a_errhmax*100, fmt='o',)
plt.plot(x,a_simhmax,lw=2)
plt.ylabel('time of max [hour]')
plt.xticks(x,myticks,rotation='vertical',size=10)

figmax = plt.figure(figsize=(15,5))
#figres.suptitle(stname,fontsize=15,fontweight='bold')
figmax.subplots_adjust(left=0.1, bottom=0.3, right=0.94, top=0.9,
                       wspace=None, hspace=None)
plt.errorbar(x, a_max, yerr=a_errmax,fmt='o',label='data')
t3 = 70
ex3 = constant.adctop*10*np.log10(1+a_simmax/t3)
plt.plot(x,ex3,lw=2,label='sim. T_sys = ' +str(t3) + ' K')
plt.xticks(x,myticks,rotation='vertical',size=10)
plt.ylabel('radio max [ADC]')
plt.legend()
    
    
plt.show()
