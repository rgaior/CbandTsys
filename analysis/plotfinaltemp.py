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
parser.add_argument("--deltatheta", type=int, nargs='?',default='0', help="delta theta")
parser.add_argument("--deltaphi", type=int, nargs='?',default='0', help="delta phi")

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

datafitfolder = constant.datafitfolder
contourfolder = constant.contourfolder
contfile = contourfolder + '/contour_' + stname + '.npz'
cont = np.load(contfile)
thetamin = cont['theta']
phimin = cont['phi']
conttheta = cont['contourtheta']
contphi = cont['contourphi']
colors = ['b','r']

print 'conttheta = ', conttheta
print 'contphi = ', contphi

theta = [0,thetamin]
phi = [0,phimin] 

factorerrtsys = cont['errtsys']
factorerrtofmax = cont['errtofmax']

fig , (ax0,ax1) = plt.subplots(2,1,figsize=(10,8),sharex=True)
fig.subplots_adjust(top=0.95,
                    wspace=None, hspace=0.01)

mintofmax = 10000
maxtofmax = -1
maxmax = -1000
minmax = 1000


errtsysfactor = 1
errtofmaxfactor =  1
ref_day = np.array([])
new_day = np.array([])
ref_tsys = np.array([])
new_tsys = np.array([])
ref_tofmax = np.array([])
ref_simtofmax = np.array([])
new_tofmax = np.array([])
new_simtofmax = np.array([])
ref_errtsys = np.array([])
new_errtsys = np.array([])
ref_errtofmax = np.array([])
new_errtofmax = np.array([])

a_turningday = np.array([])
a_turningyear = np.array([])

for t,p,c in zip(theta,phi,colors):
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
#        daycount +=1
        a_day = np.append(a_day,daycount)
        a_tsys = np.append(a_tsys,theres.tsys)
        a_errtsys = np.append(a_errtsys,theres.errortsys*factorerrtsys )
        a_sim = np.append(a_sim,theres.simmax)
        a_simtofmax = np.append(a_simtofmax,theres.simtofmax)
        a_tofmax = np.append(a_tofmax,theres.fitresult[0][2])
        a_errortofmax = np.append(a_errortofmax,theres.errortofmax*factorerrtofmax )
        a_fakeday = np.append(a_fakeday, (y-2015)*365 + d)
        a_doylist = np.append(a_doylist,str(d))
        if theres.errortofmax < 0.01:
            print 'rres.errortofmax = ' , theres.errortofmax
        if (t == 0 and p == 0):
            ref_day= np.append(ref_day, y*1000 + d)
        else:
            new_day = np.append(new_day, y*1000 + d)
    if np.min(a_tsys) < minmax:
        minmax = np.min(a_tsys)
    if np.max(a_tsys) > maxmax:
        maxmax = np.max(a_tsys)
    if np.min(a_simtofmax) < mintofmax:
        mintofmax = np.min(a_simtofmax/100)
    if np.max(a_simtofmax) > maxtofmax:
        maxtofmax = np.max(a_simtofmax/100)
    color = next(ax0._get_lines.color_cycle)
    if (t == 0 and p == 0):
        ref_tsys = a_tsys
        ref_tofmax = a_tofmax
        ref_simtofmax = a_simtofmax
        ref_errtsys = a_errtsys
        ref_errtofmax = a_errortofmax
    else:
        new_tsys = a_tsys
        new_tofmax = a_tofmax
        new_simtofmax = a_simtofmax
        new_errtsys = a_errtsys
        new_errtofmax = a_errortofmax

thedays = np.append(new_day,ref_day)    
print len(thedays), ' ', np.unique(thedays)
thedays = np.unique(thedays)
### special trick for x axis:
### find doylist:
ref_d = np.array([])
new_d = np.array([])
thedoylist = np.array([])
index_d = 0
for d in thedays:
    c = str(int(d))
    thed = int(c[4:])    
    if d in ref_day:
        ref_d  = np.append(ref_d,index_d)
    if d in new_day:
        new_d  = np.append(new_d,index_d)
    if  index_d  == 0 :
        a_turningday = np.append(a_turningday, index_d )
        a_turningyear = np.append(a_turningyear,int(d/1000))
    if index_d > 0 :
        print 'thed = ', thed , ' int(thedoylist[-1]) = ' ,int(thedoylist[-1])
        if thed < int(thedoylist[-1]):
            a_turningday = np.append(a_turningday,index_d)
            a_turningyear = np.append(a_turningyear,int(d/1000))
    thedoylist = np.append(thedoylist,str(thed))
    index_d +=1
print a_turningday, a_turningyear
print ' a_doylist = ' , a_doylist
print ' thedoylist = ' , thedoylist

ax0.plot(ref_d, ref_tsys,'.-',color='b',label= r"$\theta, \phi$ = [0 , 0]")
ax0.fill_between(ref_d, ref_tsys - ref_tsys*ref_errtsys, ref_tsys + ref_tsys*ref_errtsys,facecolor='b', alpha=0.4)        
ax0.plot(new_d, new_tsys,'.-',color='r',label= r"$\theta, \phi$ = " + '[' + str(thetamin) + ', ' + str(phimin) + ']')
ax0.fill_between(new_d, new_tsys - new_tsys*new_errtsys, new_tsys + new_tsys*new_errtsys,facecolor='r', alpha=0.4)        
ax1.plot(ref_d,ref_simtofmax/100,label=r"$\theta, \phi$ = [0, 0]",lw=2,color='b',zorder=1)
ax1.plot(new_d,new_simtofmax/100,label=r"$\theta, \phi$ = " +'['+str(thetamin) + ', ' + str(phimin) + ']',lw=2,color='r',zorder=1)
ax0.legend(ncol=2)
ax1.legend(ncol=2)
ax1.fill_between(new_d, (new_tofmax - 3) - new_errtofmax, (new_tofmax - 3) + new_errtofmax, facecolor='k', alpha=0.4,zorder=1)        
ax1.plot(new_d,(new_tofmax - 3),'.-',color='k',lw=2,label='data')
ax0.set_ylim(minmax -10,maxmax + 50)
ax0.set_xlim(0,np.max(a_day))
ax1.set_ylim(mintofmax -0.20,maxtofmax + 1.2)
ax1.set_ylabel('time of maximum [hour]')
ax0.set_ylabel('T_sys [K]')
ax1.set_xlabel('day of year')

#     ax0.plot(a_day, a_tsys,'x-',color=color,label= r"$\theta, \phi$ = " +'['+str(t) + ', ' + str(p) + ']')        
#     ax0.fill_between(a_day, a_tsys - a_tsys*a_errtsys, a_tsys + a_tsys*a_errtsys,facecolor=color, alpha=0.4)        
#     ax1.plot(a_day,a_simtofmax/100,label=r"$\theta, \phi$ = " +'['+str(t) + ', ' + str(p) + ']')

tant = 0
oneoversigmasquare = 1/((a_errtsys*a_tsys)**2)
xoversigmasquare = a_tsys*oneoversigmasquare
wmean = np.sum(xoversigmasquare)/np.sum(oneoversigmasquare)
errorwmean = np.sqrt(1/np.sum(oneoversigmasquare))
tsys = wmean + tant
print 'tsys =============== ' , tsys





plt.xticks(range(len(thedays))[::3],thedoylist[::3],rotation='vertical',size=15)

bbox_props = dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9)
for d,y in zip(a_turningday, a_turningyear):
    ax1.text(d, mintofmax+0.2, str(int(y)) , ha="left", va="center", size=15,
             bbox=bbox_props)
    ax0.text(d, 60, str(int(y)) , ha="left", va="center", size=15,
             bbox=bbox_props)
    ax0.plot(np.array([d,d]),np.array([minmax -10,maxmax + 50]),'k--',alpha=0.5)
    ax1.plot(np.array([d,d]),np.array([mintofmax -0.20,maxtofmax + 1.2]),'k--',alpha=0.5)
plt.show()


