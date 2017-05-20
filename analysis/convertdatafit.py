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
import glob
import argparse
import matplotlib as mpl

############################
##  argument parser       ##
############################
parser = argparse.ArgumentParser()
parser.add_argument("stname", type=str, nargs='?',default='popey', help="station name")

args = parser.parse_args()
#fitmethod = args.fitmethod
stname = args.stname

stname = args.stname
stid = constant.GDstationidbyname[stname]

datafolder = constant.datafolder
datafitfolder = constant.datafitfolder
files = glob.glob(datafitfolder +  '/' + str(stid) + '/res_' + stname + '_0_0_*')
outname = datafitfolder +  '/' + str(stid) + '/datafit_' + stname + '.pkl'
#out = open(outname,'w')
outdict = {}
for f in files:
    datafile = open(f,'rb')
    theres = pickle.load(datafile)    
    day = theres.day.timetuple().tm_yday
    year = theres.day.year
    print theres.fitresult[0]
    print '(year,day) = ' , year, ' ' , day
    if type(theres.fitresult[0]) is not type(0.0):
        outdict[(year,day)] = theres.fitresult
#        out.write(str(year)  + ' ' + str(day) + ' ' + str(theres.fitresult[0][0]) +' ' + str(theres.fitresult[0][0]) + ' ' + str() )

out = open(outname,'wb')
pickle.dump(outdict,out)                                                                                                                                                      
out.close()   


fitfile = open(outname,'rb')
fitdict = pickle.load(fitfile)
#print fitdict
for d in [63]:
    print fitdict[(2015,d)]
    
