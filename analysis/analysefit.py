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
import datetime
import constant
import utils
import fitresult
import argparse

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

#thetas = [0]
#phis = [0]
thetas = range(-30,30,2)
phis = range(-30,30,2)
a_meanchi2 = np.array([])
a_len= np.array([])
a_thetas= np.array([])
a_phis= np.array([])
for t in thetas:
    for p in phis:
        a_thetas = np.append(a_thetas, t)
        a_phis = np.append(a_phis, p)
        print 't = ' , t, ' p =  ', p
        a_chi2 = np.array([])
        a_erra = np.array([])
        a_eval = np.array([])
        for y,d in zip(goodyear,goodday):
            y = int(y)
            d = int(d)
#fit2_popey_-30_-30_2015_63.txt
            fitfilename = constant.datafit2folder + '/' + str(stid) + '/fit2_' + stname + '_' +str(t) + '_' + str(p) + '_' + str(y) + '_' + str(d) + '.txt'
            if os.path.isfile(fitfilename):
#                print fitfilename
                fr = fitresult.Fitresult(fitfilename)                
                fr.fill()
                a_chi2 = np.append(a_chi2,fr.redchi2)
                a_erra = np.append(a_erra,fr.erra)
                a_eval = np.append(a_eval,fr.funceval)
            else:
                continue
        a_meanchi2 = np.append(a_meanchi2,np.mean(a_chi2[a_erra>0]))
        a_len = np.append(a_len,len(a_chi2[a_erra>0]))

print 'len(a_meanchi2) = ', len(a_meanchi2)
print 'len(a_len) = ' , len(a_len) 
print 'len(thetas) = ' , len(thetas) 
print 'len(phis) = ' , len(phis) 

fig = plt.figure()
plt.scatter(a_thetas, a_phis, s=200,c=a_meanchi2)
plt.colorbar()
fig2 = plt.figure()
plt.scatter(a_thetas, a_phis, s=200,c=a_len)
plt.colorbar()

plt.show()
