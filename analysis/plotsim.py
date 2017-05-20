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

deltathetas = [0]
deltaphis = [0]
a_chi2 = np.array([])
#for y,d in zip(goodyear[::10],goodday[::10]):
goodyear = [2016]
goodday = [10]
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
            ########################
            ####### simulation #####
            ########################

            simfile = constant.simresultfolder + str(stid) + '/exptemp_' + stname + '_0_0_' + str(y) + '_' + str(d) + '.txt'
            [h,m,temp] = utils.readtempfile(simfile)
            sec = 3600*h + 60*m    
            hour = h*100 + m*(100./60.)
            plt.plot(hour, temp)


plt.show()
