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
import glob
############################
##  argument parser       ##
############################
parser = argparse.ArgumentParser()
parser.add_argument("stname", type=str, nargs='?',default='popey', help="station name")
parser.add_argument("-list", type=str, help="list of good days")

args = parser.parse_args()
stname = args.stname

stname = args.stname
stid = constant.GDstationidbyname[stname]
if args.list:
    listfile = args.list
    goodlistname = listfile
else:
    goodlistname = 'newlist_' + stname + '.txt'
[goodyear,goodday] = utils.getdaysfromlist(constant.listfolder + goodlistname)

datafitfolder = constant.datafitfolder
contourfolder = constant.contourfolder
contfile = contourfolder + '/contour_' + stname + '.npz'
cont = np.load(contfile)
thetamin = cont['theta']
phimin = cont['phi']
conttheta = cont['contourtheta']
contphi = cont['contourphi']

print 'conttheta = ', conttheta
print 'contphi = ', contphi

factorerrtsys = cont['errtsys']
factorerrtofmax = cont['errtofmax']

theta = [0,6, 9]
phi = [0,-4, -30] 

fig , (ax0,ax1) = plt.subplots(2,1,figsize=(10,8),sharex=True)
fig.subplots_adjust(top=0.95,
                    wspace=None, hspace=0.01)

mintofmax = 10000
maxtofmax = -1
maxmax = -1000
minmax = 1000


#errtsysfactor = 1
#errtofmaxfactor =  1

for t,p in zip(theta,phi):
    a_tsys = np.array([])
    a_errtsys = np.array([])
    a_tofmax = np.array([])
    a_errortofmax = np.array([])
    a_simtofmax = np.array([])
    a_sim = np.array([])
    a_doylist = np.array([])
    a_fakeday = np.array([])
    a_day = np.array([])
    daycount = 0
    allday = np.linspace(1,len(goodyear),len(goodyear))
    for y,d  in zip(goodyear,goodday):
        y = int(y)
        d = int(d)
        fname = constant.datafitfolder + '/' + str(stid) + '/res_' + stname + '_0_0_' + str(y) + '_' + str(d) +'.pkl'
        if os.path.isfile(fname):
            datafile = open(fname,'rb')
        else:
            continue
        theres = pickle.load(datafile)    
            ########################
            ####### simulation #####
            ########################
        simfile = constant.simresultfolder + str(stid) + '/exptemp_' + stname + '_' +str(t) + '_' + str(p) + '_' + str(y) + '_' + str(d) + '.txt'
        [h,m,temp] = utils.readtempfile(simfile)
        sec = 3600*h + 60*m    
        hour = h*100 + m*(100./60.)
        theres.datasim.sim = temp
        theres.datasim.timesim = hour
        day = utils.doytodate(y,d)
        theres.theta = t
        theres.phi = p
        simparam = theres.getsimparam()
        if type(theres.fitresult[0]) is not type(0.0):        
            theres.computetsys()
            theres.geterrorsonfit()
        if np.isnan(theres.errortsys) or np.isnan(theres.tsys) or np.isnan(theres.fitresult[0][2]) or np.isnan(theres.errortofmax): 
            continue
        if np.isinf(theres.errortsys) or np.isinf(theres.tsys) or np.isinf(theres.fitresult[0][2]) or np.isinf(theres.errortofmax): 
            continue
        if ( theres.tsys < 20 ) or ( theres.tsys > 120 )  :
            continue
        daycount +=1
        a_day = np.append(a_day,daycount)
        a_tsys = np.append(a_tsys,theres.tsys)
        a_errtsys = np.append(a_errtsys,theres.errortsys*factorerrtsys)
        a_sim = np.append(a_sim,theres.simmax)
        a_simtofmax = np.append(a_simtofmax,theres.simtofmax)
        a_tofmax = np.append(a_tofmax,theres.fitresult[0][2])
        a_errortofmax = np.append(a_errortofmax,theres.errortofmax*factorerrtofmax)
        a_fakeday = np.append(a_fakeday, (y-2015)*365 + d)
        a_doylist = np.append(a_doylist,str(d))
        if theres.errortofmax < 0.01:
            print 'rres.errortofmax = ' , theres.errortofmax


    if np.min(a_tsys) < minmax:
        minmax = np.min(a_tsys)
    if np.max(a_tsys) > maxmax:
        maxmax = np.max(a_tsys)
    if np.min(a_simtofmax) < mintofmax:
        mintofmax = np.min(a_simtofmax/100)
    if np.max(a_simtofmax) > maxtofmax:
        maxtofmax = np.max(a_simtofmax/100)
    color = next(ax0._get_lines.color_cycle)
    ax0.plot(a_day, a_tsys,'x-',color=color,label= r"$\theta, \phi$ = " +'['+str(t) + ', ' + str(p) + ']')        
    ax0.fill_between(a_day, a_tsys - a_tsys*a_errtsys, a_tsys + a_tsys*a_errtsys,facecolor=color, alpha=0.4)        
    ax1.plot(a_day,a_simtofmax/100,label=r"$\theta, \phi$ = " +'['+str(t) + ', ' + str(p) + ']')

tant = 0
oneoversigmasquare = 1/((a_errtsys*a_tsys)**2)
xoversigmasquare = a_tsys*oneoversigmasquare
wmean = np.sum(xoversigmasquare)/np.sum(oneoversigmasquare)
errorwmean = np.sqrt(1/np.sum(oneoversigmasquare))
tsys = wmean + tant
print 'tsys =============== ' , tsys

    
ax1.plot(a_day,(a_tofmax - 3),'x-',color='k',lw=2,label='data')
ax1.fill_between(a_day, (a_tofmax - 3) - a_errortofmax, (a_tofmax - 3) + a_errortofmax, facecolor='k', alpha=0.4)        
#ax1.plot(a_day,(a_tofmax),'x-',color='k',lw=2,label='data')
#ax1.fill_between(a_day, (a_tofmax) - a_errortofmax, (a_tofmax ) + a_errortofmax, facecolor='k', alpha=0.4)        
ax0.legend(ncol=2)
ax1.legend(ncol=2)
ax0.set_ylim(minmax -10,maxmax + 50)
ax0.set_xlim(0,np.max(a_day))
ax1.set_ylim(mintofmax -0.20,maxtofmax + 1.2)
ax1.set_ylabel('time')
ax0.set_ylabel('T_sys [K]')
ax1.set_xlabel('doy')
#plt.xticks(allday[::3],a_doylist[::3],rotation='vertical',size=15)
plt.xticks(a_day[::3],a_doylist[::3],rotation='vertical',size=15)
plt.show()
