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
parser.add_argument("--fitmethod", type=int, nargs='?',default='0', help="")
args = parser.parse_args()
stname = args.stname
fitmethod= args.fitmethod
stid = constant.GDstationidbyname[stname]

resfolder = constant.resfolder
theta = range(-30,30,1)
phi = range(-30,30,1)

a_chi2_tsys = np.ndarray(shape=(len(phi), len(theta) ))
a_chi2_tofmax = np.ndarray(shape=(len(phi), len(theta) ))
a_chi2_all = np.ndarray(shape=(len(phi), len(theta) ))
a_nroffit = np.ndarray(shape=(len(phi), len(theta) ))

chi2allmin = 1000
thetamin = 0
phimin = 0
newt,newp = np.meshgrid(theta,phi)
print newt
print newp

phiiter = range(0,len(newp),1)
fname = constant.mainfolder + '/results/' + '/res_'+ stname + '.npz'
file = np.load(fname)
ftheta = file['theta']
fphi = file['phi']
fchi2tsys = file['chi2tsys']
fchi2tofmax = file['chi2tofmax']
fnroffit = file['fits']
maxnroffit = np.max(fnroffit)


newnroffit = np.array([])
# first pass to find the minimum chi2
minchi2tsys = 1000
minchi2tofmax = 1000

minthetatsys = 0
minphitsys = 0
minthetatofmax = 0
minphitofmax = 0


chiallmin = 1000
mintheta = 0
minphi = 0

factorfits = 0.95
for iter in phiiter:
    phi_chi2 = np.array([])
    tcount = 0
    for t,p in zip(newt[iter],newp[iter]):
        index = np.where( (ftheta == t) & (fphi == p) )
        thet = ftheta[index]
        thep = fphi[index]
        thechi2tsys = fchi2tsys[index]
        thechi2tofmax = fchi2tofmax[index]
        thenroffit = fnroffit[index]
        print 'thenroffit = ' , thenroffit , 'maxnroffit = ' , maxnroffit
        if (thenroffit < factorfits*maxnroffit) or np.isnan(thechi2tsys) or np.isnan(thechi2tofmax):
            thechi2tsys = 1000
            thechi2tofmax = 1000

        if thechi2tsys < minchi2tsys:
            minchi2tsys = thechi2tsys
            minthetatsys  = thet
            minphitsys  = thep
        if thechi2tofmax < minchi2tofmax:
            minchi2tofmax = thechi2tofmax
            minthetatofmax  = thet
            minphitofmax  = thep


print 'minchi2tsys = ' , minchi2tsys 
print 'minchi2tofmax = ' , minchi2tofmax
print 'minthetatofmax = ' , minthetatofmax

for iter in phiiter:
    phi_chi2 = np.array([])
    tcount = 0
    for t,p in zip(newt[iter],newp[iter]):
        index = np.where( (ftheta == t) & (fphi == p) )
        thet = ftheta[index]
        thep = fphi[index]
        thechi2tsys = fchi2tsys[index]
        thechi2tofmax = fchi2tofmax[index]
        thenroffit = fnroffit[index]
        if (thenroffit < factorfits*maxnroffit):
            thechi2tsys = 1000
            thechi2tofmax = 1000
        chi2all = thechi2tofmax/minchi2tofmax + thechi2tsys/minchi2tsys
        a_chi2_tsys[iter][tcount] = thechi2tsys/minchi2tsys
        a_chi2_tofmax[iter][tcount] = thechi2tofmax/minchi2tofmax
        a_chi2_all[iter][tcount] = chi2all
        a_nroffit[iter][tcount] = thenroffit
        if chi2all < chi2allmin:
            chi2allmin = chi2all
            mintheta = t
            minphi = p
        tcount +=1


#levels = np.array([2,10,100])
levels = np.array([2,4,6])
ftsys = plt.figure(figsize=(8,8))
CS = plt.contour(newt,newp,a_chi2_tsys,levels,colors=('#000066', '#0066ff',  '#00cc00'))
plt.xlabel(r'$\delta \theta $ [deg]')
plt.ylabel(r'$\delta \phi $ [deg]')
plt.clabel(CS, inline=1, fontsize=10)
plt.title('system temperature = constante')
ftofmax = plt.figure(figsize=(8,8))
CS2 = plt.contour(newt,newp,a_chi2_tofmax,levels,colors=('#000066', '#0066ff',  '#00cc00'))
plt.clabel(CS2, inline=1, fontsize=10)
plt.xlabel(r'$\delta \theta $ [deg]')
plt.ylabel(r'$\delta \phi $ [deg]')
plt.title('time of max')
fall = plt.figure(figsize=(8,8))
fall.suptitle(stname, fontsize=15, fontweight='bold')
CS3 = plt.contour(newt,newp,a_chi2_all/2,levels,colors=('#000066', '#0066ff',  '#00cc00'))
plt.clabel(CS3, inline=1, fontsize=10)
plt.xlabel(r'$\delta \theta $ [deg]')
plt.ylabel(r'$\delta \phi $ [deg]')
plt.title('combined: system temperature and time of max ')

plt.plot(mintheta,minphi,'o',color='k')
print 'mintheta = ', mintheta,  ' minphi = ' , minphi  
print len(CS3.collections[0].get_paths())
xcont = np.array([])
ycont = np.array([])
for path in CS3.collections[0].get_paths():
#for path in CS3.collections[0].get_paths()[:2]:
    v = path.vertices
    xcont = np.append(xcont,v[:,0])
    ycont = np.append(ycont,v[:,1])
    print v
outfinalres = constant.contourfolder + '/contour_' + stname

np.savez(outfinalres,theta=mintheta, phi=minphi, errtsys = np.sqrt(minchi2tsys), errtofmax = np.sqrt(minchi2tofmax), contourtheta = xcont, contourphi = ycont)

plt.show()
