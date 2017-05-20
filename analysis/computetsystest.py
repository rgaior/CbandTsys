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

#deltathetas = range(-30,30,10)
#deltaphis = range(-30,30,10)
deltathetas = [-23]
deltaphis = [-10]

a_chi2 = np.array([])
#for y,d in zip(goodyear[::10],goodday[::10]):

mintofmax = 10000
maxtofmax = -1
maxmax = -1000
minmax = 1000
a_chi2tofmax = np.array([])
a_nroffit = np.array([])
a_chi2tsys = np.array([])
a_chi2all = np.array([])
a_theta = np.array([])
a_phi = np.array([])


for t in deltathetas:
    for p in deltaphis:
#for t in [0]:
#    for p in [0]:
        print 't = ' , t , ' p = ' , p
        a_tsys = np.array([])
        a_errtsys = np.array([])
        a_tofmax = np.array([])
        a_errortofmax = np.array([])
        a_simtofmax = np.array([])
        a_sim = np.array([])
        a_doylist = np.array([])
        for y,d  in zip(goodyear,goodday):
            y = int(y)
            d = int(d)
            print ' year = ',  y , ' day = ' ,d
            fname = constant.datafitfolder + '/' + str(stid) + '/res_' + stname + '_0_0_' + str(y) + '_' + str(d) +'.pkl'
#            fname = constant.datafitfolder + '/' + str(stid) + '/res_' + stname + '_' + str(t) + '_' + str(p) + '_' + str(y) + '_' + str(d) +'.pkl'
            a_doylist = np.append(a_doylist,str(d))
            if os.path.isfile(fname):
                datafile = open(fname,'rb')
            else:
                continue
            theres = pickle.load(datafile)    
            ########################
            ####### simulation #####
            ########################
#            simfile = constant.simresultfolder + str(stid) + '/exptemp_' + stname + '_0_0_' + str(y) + '_' + str(d) + '.txt'
            simfile = constant.simresultfolder + str(stid) + '/exptemp_' + stname + '_' +str(t) + '_' + str(p) + '_' + str(y) + '_' + str(d) + '.txt'
#            print simfile
            [h,m,temp] = utils.readtempfile(simfile)
#            print np.max(temp)
            sec = 3600*h + 60*m    
            hour = h*100 + m*(100./60.)
            theres.datasim.sim = temp
            theres.datasim.timesim = hour
            day = utils.doytodate(y,d)
            theres.theta = t
            theres.phi = p
            simparam = theres.getsimparam()
            print ' poptsim = ' , simparam
            
            if type(theres.fitresult[0]) is not type(0.0):        
#                print ' inside  ', theres.fitresult
                theres.computetsys()
                theres.geterrorsonfit()
 #               hourarray = utils.gethourarray(theres.datasim.timedata)        
#                an.goodfit = True
#                print ' tsys = ' , theres.tsys 
            if np.isnan(theres.errortsys) or np.isnan(theres.tsys) or np.isnan(theres.fitresult[0][2]) or np.isnan(theres.errortofmax): 
#                print ' hhahahahahah du nan  ' 
                continue
            if np.isinf(theres.errortsys) or np.isinf(theres.tsys) or np.isinf(theres.fitresult[0][2]) or np.isinf(theres.errortofmax): 
#                print ' hhahahahahah du inf  ' 
                continue
            if ( theres.tsys < 1):
#                print 'tsys < 1 ' , theres.tsys
                continue
            a_tsys = np.append(a_tsys,theres.tsys)
            a_errtsys = np.append(a_errtsys,theres.errortsys)
            a_sim = np.append(a_sim,theres.simmax)
            a_simtofmax = np.append(a_simtofmax,theres.simtofmax)
            a_tofmax = np.append(a_tofmax,theres.fitresult[0][2])
            a_errortofmax = np.append(a_errortofmax,theres.errortofmax)
            if theres.errortofmax < 0.01:
                print 'rres.errortofmax = ' , theres.errortofmax
            nroffit = len(a_errortofmax)
        
#        if nroffit < 0.8*constant.nroffitmax[stname] :
#            continue

        deltat = a_simtofmax/100 - a_tofmax +3
        chi2tofmax = np.sum((deltat)**2 / (a_errortofmax)**2)
        chi2tofmax = chi2tofmax / len(a_errortofmax)
        ###########################
        ## compute Tsys  ##########
        ###########################
        tant = 0
        oneoversigmasquare = 1/((a_errtsys*a_tsys)**2)
        xoversigmasquare = a_tsys*oneoversigmasquare
        wmean = np.sum(xoversigmasquare)/np.sum(oneoversigmasquare)
        errorwmean = np.sqrt(1/np.sum(oneoversigmasquare))
        tsys = wmean + tant
        chi2tsys = np.sum((a_tsys - tsys)**2/ (a_errtsys*a_tsys)**2 )
        chi2tsys = chi2tsys/len(a_errortofmax)
        chi2all = chi2tofmax + chi2tsys
        
#        print 'deltat = ' , deltat
#        print ' a_errortofmax = ' , a_errortofmax
#        print chi2
        a_chi2tofmax = np.append(a_chi2tofmax,chi2tofmax)
        a_chi2tsys = np.append(a_chi2tsys,chi2tsys)
        a_chi2all = np.append(a_chi2all,chi2all)
        a_theta = np.append(a_theta,t)
        a_phi = np.append(a_phi,p)
        a_nroffit = np.append(a_nroffit,len(a_errortofmax))

print 'minimum chi2 tsys = ' , np.min(a_chi2tsys)
print 'minimum chi2 tofmax = ' , np.min(a_chi2tofmax)
amintsys = np.argmin(a_chi2tsys)
amintofmax = np.argmin(a_chi2tofmax)
print 'Tsys: theta min  =  ', a_theta[amintsys], ' phi min = ', a_phi[amintsys]
print 'Tofmax: theta min  =  ', a_theta[amintofmax], ' phi min = ', a_phi[amintofmax]

print 'nroffit max = ' , np.max(a_nroffit)

#resultfile = constant.resfolder +  '/res_'+stname
#np.savez(resultfile,theta=a_theta, phi=a_phi,fits=a_nroffit,chi2tsys = a_chi2tsys,chi2tofmax=a_chi2tofmax)


#print a_chi2tsys
#plt.scatter(a_theta,a_phi,s=200,c=a_chi2all,vmin=np.min(a_chi2all),vmax=np.min(a_chi2all) + 2)
fig = plt.figure()
plt.scatter(a_theta,a_phi,s=200,c=a_chi2tsys,vmin=np.min(a_chi2tsys),vmax=np.min(a_chi2tsys) + 10 )
plt.colorbar()
fig2 = plt.figure()
plt.scatter(a_theta,a_phi,s=200,c=a_chi2tofmax,vmin=np.min(a_chi2tofmax),vmax=np.min(a_chi2tofmax) + 10)
#plt.scatter(a_theta,a_phi,s=200,c=a_chi2,vmin=np.min(a_chi2),vmax=np.min(a_chi2) + 2)
plt.xlabel('delta theta [deg]')
plt.ylabel('delta phi [deg]')
plt.colorbar()

fig3 = plt.figure()
plt.scatter(a_theta,a_phi,s=200,c=a_nroffit,vmin=np.min(a_nroffit),vmax=np.max(a_nroffit))
#plt.scatter(a_theta,a_phi,s=200,c=a_chi2,vmin=np.min(a_chi2),vmax=np.min(a_chi2) + 2)
plt.xlabel('delta theta [deg]')
plt.ylabel('delta phi [deg]')
print 'a_nroffit, = ', a_nroffit
print 'a_chi2tsys = ', a_chi2tsys
print 'a_chi2tofmax  = ', a_chi2tofmax
plt.colorbar() 

        
plt.show()


# #    it +=1
    
    
# figchi2 = plt.figure()
# figchi2.suptitle(stname)
# plt.hist(a_chi2,bins=50)
# plt.xlabel('chi 2')
# plt.show()
