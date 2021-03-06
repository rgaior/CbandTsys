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
a_chi2tsys = np.array([])
a_chi2tofmax = np.array([])
a_len = np.array([])
a_thetas = np.array([])
a_phis = np.array([])
a_finalthetas = np.array([])
a_finalphis = np.array([])
a_chi2tsys = np.array([])
a_chi2tofmax = np.array([])
for t in thetas:
    for p in phis:
        a_thetas = np.append(a_thetas, t)
        a_phis = np.append(a_phis, p)
        print 't = ' , t, ' p =  ', p
        a_chi2 = np.array([])
        a_erra = np.array([])
        a_eval = np.array([])
        a_tsys = np.array([])
        a_errtsys = np.array([])
        a_errpostsys = np.array([])
        a_errnegtsys = np.array([])
        a_tofmax = np.array([])
        a_errtofmax = np.array([])
        a_simtsys = np.array([])
        a_simtofmax = np.array([])
        a_day = np.array([])
        day = 0
        for y,d in zip(goodyear,goodday):
            y = int(y)
            d = int(d)
            fitfilename = constant.datafit2folder + '/' + str(stid) + '/fit2_' + stname + '_' +str(t) + '_' + str(p) + '_' + str(y) + '_' + str(d) + '.txt'
            if os.path.isfile(fitfilename):
                fr = fitresult.Fitresult(fitfilename)                
                fr.fill()
#                print fr.erra
                if fr.erra < 1:
                    continue
                if float(fr.erra)/float(fr.a) > 0.5:
                    continue
#                print 'float(fr.erra)/float(fr.a) = ', float(fr.erra)/float(fr.a)
                if fr.redchi2 > 20:
                    continue
                a_chi2 = np.append(a_chi2,fr.redchi2)
                a_erra = np.append(a_erra,fr.erra)
                a_eval = np.append(a_eval,fr.funceval)

                
                simfile = constant.simresultfolder + str(stid) + '/exptemp_' + stname + '_'+str(t) + '_' + str(p) + '_' + str(y) + '_' + str(d) + '.txt'
                [h,m,temp] = utils.readtempfile(simfile)
                sec = 3600*h + 60*m    
                hour = h*100 + m*(100./60.)
                simtofmax = hour[np.argmax(temp)]
                a_simtofmax = np.append(a_simtofmax, simtofmax)

                tsys = utils.adctotsys(fr.a,np.max(temp))
                tsysplus = utils.adctotsys(fr.a - fr.erra,np.max(temp))
                tsysminus = utils.adctotsys(fr.a + fr.erra,np.max(temp))                
                a_tsys = np.append(a_tsys,tsys)
                a_errtsys = np.append(a_errtsys, (tsysplus - tsysminus)/2)
                a_errpostsys = np.append(a_errpostsys,tsysplus)
                a_errnegtsys = np.append(a_errnegtsys,tsysminus)
                a_tofmax = np.append(a_tofmax, fr.mu)
                a_errtofmax = np.append(a_errtofmax, fr.errmu)
                a_day = np.append(a_day,day)
                day +=1
#                print 'funceval = ', fr.funceval
#                print 'tsys = ', tsys , ' + ', tsysplus - tsys, ' - ',tsys - tsysminus 

            else:
                continue
#        a_meanchi2 = np.append(a_meanchi2,np.mean(a_chi2[a_erra>0]))
#        a_len = np.append(a_len,len(a_chi2[a_erra>0]))

        deltat = a_simtofmax/100 - a_tofmax + 3
#        print 'deltat = ', deltat
#        print 'a_simtofmax = ', a_simtofmax
#        print 'a_tofmax = ', a_tofmax
        chi2tofmax = np.sum((deltat)**2 / (a_errtofmax)**2)
        chi2tofmax = chi2tofmax / len(a_errtofmax)
        ###########################
        ## compute Tsys  ##########
        ###########################
        tant = 0
#        print 'a_tsys = ' , a_tsys
#        print 'a_errtsys = ', a_errtsys
        oneoversigmasquare = 1/((a_errtsys)**2)
        xoversigmasquare = a_tsys*oneoversigmasquare
        wmean = np.sum(xoversigmasquare)/np.sum(oneoversigmasquare)
        errorwmean = np.sqrt(1/np.sum(oneoversigmasquare))
        tsys = wmean + tant
        chi2tsys = np.sum((a_tsys - tsys)**2/ (a_errtsys)**2 )
        chi2tsys = chi2tsys/len(a_errtofmax)
        if len(a_errtofmax) < 30:
            continue
        a_finalthetas = np.append(a_finalthetas, t)
        a_finalphis = np.append(a_finalphis, p)
        a_chi2tsys = np.append(a_chi2tsys,chi2tsys)
        a_chi2tofmax = np.append(a_chi2tofmax,chi2tofmax)
        chi2all = chi2tofmax + chi2tsys
        print ' tsys = ', tsys  , ' +- ', errorwmean
        print 'length = ', len(a_errtofmax)
        print 'chi2tsys  = ', chi2tsys
#        print 'a_tsys  = ', a_tsys
#        print 'a_errtsys  = ', a_errtsys
        print 'chi2tofmax  = ', chi2tofmax
        



print 'len(a_meanchi2) = ', len(a_meanchi2)
print 'len(a_len) = ' , len(a_len) 
print 'len(thetas) = ' , len(thetas) 
print 'len(phis) = ' , len(phis) 
fig = plt.figure()
plt.scatter(a_finalthetas, a_finalphis, s=200,c=a_chi2tsys)
#plt.scatter(a_thetas, a_phis, s=200,c=a_meanchi2)
plt.colorbar()
fig2 = plt.figure()
plt.scatter(a_finalthetas, a_finalphis, s=200,c=a_chi2tofmax)
#plt.scatter(a_thetas, a_phis, s=200,c=a_len)
plt.colorbar()

plt.show()
