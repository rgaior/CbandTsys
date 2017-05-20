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
stid = constant.GDstationidbyname[stname]
if args.list:
    listfile = args.list
    goodlistname = listfile
else:
    goodlistname = 'newlist_' + stname + '.txt'
#goodlistname = stname + '.txt'
[goodyear,goodday] = utils.getdaysfromlist(constant.listfolder + goodlistname)


contourfolder = constant.contourfolder
contfile = contourfolder + '/contour_' + stname + '.npz'
cont = np.load(contfile)
thetamin = cont['theta']
phimin = cont['phi']
print 'thetamin = ' , thetamin, ' phi min = ',  phimin
conttheta = cont['contourtheta']
contphi = cont['contourphi']
#print 'conttheta = ', conttheta
#print 'contphi = ', contphi

factorerrtsys = cont['errtsys']
factorerrtofmax = cont['errtofmax']

a_tsys = np.array([])
a_errtsys = np.array([])
a_tofmax = np.array([])
a_errtofmax = np.array([])
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
    simfile = constant.simresultfolder + str(stid) + '/exptemp_' + stname + '_' +str(thetamin) + '_' + str(phimin) + '_' + str(y) + '_' + str(d) + '.txt'
    [h,m,temp] = utils.readtempfile(simfile)
    sec = 3600*h + 60*m    
    hour = h*100 + m*(100./60.)
    theres.datasim.sim = temp
    theres.datasim.timesim = hour
    day = utils.doytodate(y,d)
    theres.theta = thetamin
    theres.phi = phimin
    simparam = theres.getsimparam()
    if type(theres.fitresult[0]) is not type(0.0):        
        theres.computetsys()
        theres.geterrorsonfit()
    if np.isnan(theres.errortsys) or np.isnan(theres.tsys) or np.isnan(theres.fitresult[0][2]) or np.isnan(theres.errortofmax): 
        continue
    if np.isinf(theres.errortsys) or np.isinf(theres.tsys) or np.isinf(theres.fitresult[0][2]) or np.isinf(theres.errortofmax): 
        continue
    if ( theres.tsys < 20 ) or ( theres.tsys > 120 )  :
    #if ( theres.tsys < 1):
        continue


    a_tsys = np.append(a_tsys,theres.tsys)
    a_errtsys = np.append(a_errtsys,factorerrtsys*theres.errortsys)
    a_tofmax = np.append(a_tofmax,theres.fitresult[0][2])
    a_errtofmax = np.append(a_errtofmax,factorerrtofmax*theres.errortofmax)
    
tant = 0
thetsys = 0 
oneoversigmasquare = 1/((a_errtsys*a_tsys)**2)
xoversigmasquare = a_tsys*oneoversigmasquare
wmean = np.sum(xoversigmasquare)/np.sum(oneoversigmasquare)
theerrorwmean = np.sqrt(1/np.sum(oneoversigmasquare))
thetsys = wmean + tant

print 'corrected tsys =============== ' , thetsys ,' +-' ,theerrorwmean


#########################
### find systematics ####
#########################
thetas =conttheta.astype(int) 
phis =contphi.astype(int) 
print thetas, phis
maxtsys = 0
mintsys = 1000
for t,p in zip(thetas,phis):
    print 't = ', t , ' p = ' , p
    a_tsys = np.array([])
    a_errtsys = np.array([])
    a_tofmax = np.array([])
    a_errtofmax = np.array([])
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
        theres.theta = thetamin
        theres.phi = phimin
        simparam = theres.getsimparam()
        if type(theres.fitresult[0]) is not type(0.0):        
            theres.computetsys()
            theres.geterrorsonfit()
        if np.isnan(theres.errortsys) or np.isnan(theres.tsys) or np.isnan(theres.fitresult[0][2]) or np.isnan(theres.errortofmax): 
            continue
        if np.isinf(theres.errortsys) or np.isinf(theres.tsys) or np.isinf(theres.fitresult[0][2]) or np.isinf(theres.errortofmax): 
            continue
        if ( theres.tsys < 20 ) or ( theres.tsys > 120 )  :
#        if ( theres.tsys < 1):
            continue


        a_tsys = np.append(a_tsys,theres.tsys)
        a_errtsys = np.append(a_errtsys,factorerrtsys*theres.errortsys)
        a_tofmax = np.append(a_tofmax,theres.fitresult[0][2])
        a_errtofmax = np.append(a_errtofmax,factorerrtofmax*theres.errortofmax)
        
    print 'a_tsys = ',  a_tsys
    tant = 0
    tsys = 0 
    oneoversigmasquare = 1/((a_errtsys*a_tsys)**2)
    xoversigmasquare = a_tsys*oneoversigmasquare
    wmean = np.sum(xoversigmasquare)/np.sum(oneoversigmasquare)
    errorwmean = np.sqrt(1/np.sum(oneoversigmasquare))
    tsys = wmean + tant

    print 'tsys =============== ' , tsys ,' +-' ,errorwmean
    if tsys > maxtsys:
        maxtsys = tsys
    if tsys < mintsys:
        mintsys = tsys
            
print 'Temperature = ' , thetsys , '+- ', theerrorwmean, ' +' , maxtsys -thetsys , ' - ' , thetsys  - mintsys 
print 'np.max(thetas) = ' ,np.max(thetas)
print 'and angle informations: thetamin = ' , thetamin, ' + ' , np.max(thetas) - thetamin ,' - ' , thetamin - np.min(thetas),  ' phimin = ',  phimin,  ' + ' , np.max(phis) - phimin ,' - ' , phimin - np.min(phis)













#     print ' theta = ' ,t , ' phi = ' , p
#     a_tsys = np.array([])
#     a_errtsys = np.array([])
#     a_tofmax = np.array([])
#     a_errtofmax = np.array([])
#     for y,d  in zip(goodyear,goodday):
#         y = int(y)
#         d = int(d)
#         fname = resfolder + '/res_' + stname + '_' + str(t) + '_' + str(p) + '_' + str(y) + '_' + str(d) +'.pkl'
#         if os.path.isfile(fname):
#             datafile = open(fname,'rb')
#         else:
#             continue
#         res = pickle.load(datafile)        
#         if np.isnan(res.errortsys) or np.isnan(res.tsys) or np.isnan(res.fitresult[0][2]) or np.isnan(res.errortofmax): 
#             continue
#         if np.isinf(res.errortsys) or np.isinf(res.tsys) or np.isinf(res.fitresult[0][2]) or np.isinf(res.errortofmax): 
#             continue
#         if ( res.tsys < 1):
#             continue
#         a_tsys = np.append(a_tsys,res.tsys)
#         a_errtsys = np.append(a_errtsys,factorerrtsys*res.errortsys)
#         a_tofmax = np.append(a_tofmax,res.fitresult[0][2])
#         a_errtofmax = np.append(a_errtofmax,factorerrtofmax*res.errortofmax)

#     tant = 0 
#     tsys =0 
#     oneoversigmasquare = 1/((a_errtsys*a_tsys)**2)
#     xoversigmasquare = a_tsys*oneoversigmasquare
#     wmean = np.sum(xoversigmasquare)/np.sum(oneoversigmasquare)
#     errorwmean = np.sqrt(1/np.sum(oneoversigmasquare))
#     tsys = wmean + tant
