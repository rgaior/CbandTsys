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
from lmfit import Model, Parameters
import dataset
import daydata
import math
import datetime
import pickle
import numpy as np
from numpy.linalg import inv
import os
import sys
cwd = os.getcwd()
utilspath = cwd + '/../utils/'
sys.path.append(utilspath)
import utils
import constant
import daydata

class Analyse:
    def __init__(self, day = None, theta=0, phi=0, datasim = None):
        self.day = day
        self.phi = phi # phi angle shift from nominal antenna position
        self.theta = theta # theta angle shift from nominal antenna position
        self.datasim = datasim # the data and simulation object (daydata object)
        self.simtofmax = 0 # time of maximum in simulation 
        self.simwidth= 0 # width of simulation 
        self.simmax= 0 # max of simulation 
        self.cbaseline = np.array([]) # baseline corrected and ready for sun signal fit        
        self.pointuncert = 0 # uncertainty on each point of the baseline
        self.fitresult = [0,0] # [popt, pcov] for the data sun signal fit
        self.goodfit = True
        self.tsys = 0
        self.errortsys = 0
        self.errortofmax = 0


    def getsimparam(self):
        self.simtofmax = self.datasim.timesim[np.argmax(self.datasim.sim)]
        max = np.max(self.datasim.sim)
        width = 150
        [poptsim,pcovsim] = utils.fitwithexpo0noerr(self.datasim.timesim, self.datasim.sim, max, width,self.simtofmax,0)
        if type(poptsim) == type(0.0):
            self.simwidth = 1.50
        else:
            self.simwidth = poptsim[1]/100
        self.simmax = np.max(self.datasim.sim)
#        print self.simwidth
#        print ' self.simmax  = ' , self.simmax 
        return poptsim
    
    def getsimvalueatdatamax(self):
        datatofmax = self.fitresult[0][2]
        datatofmax = (datatofmax - 3)*100
#        print ' datatofmax = ' , datatofmax
#        print ' self.simtofmax =  ', self.simtofmax
        simval = np.interp(datatofmax,self.datasim.timesim, self.datasim.sim)
#        print 'sim val at time of max data = ' , simval
#        print 'self.simmax = ', self.simmax
        return  simval
        

    def correctbaseline(self,nameofstation):
        timeofsunmax = self.simtofmax/100 # time in HH.hh (13.66 = 13h40) instead of HHhh (1366 = 13h40)
#        print 'timeofsunmax = ' , timeofsunmax
#        print 't1 = ' , int(timeofsunmax - 2),  ' ' ,  int(np.modf(timeofsunmax - 2)[0]*60)
#        t1 = utils.doytodate(self.day.year,self.day.day,int(timeofsunmax - 2), int(np.modf(timeofsunmax - 2)[0]*60))
#        t2 = utils.doytodate(self.day.year,self.day.day,int(timeofsunmax + 2), int(np.modf(timeofsunmax + 2)[0]*60))
        t1 = utils.doytodate(self.day.year,self.day.timetuple().tm_yday, int(timeofsunmax - 4), int(np.modf(timeofsunmax - 4)[0]*60))
        t2 = utils.doytodate(self.day.year,self.day.timetuple().tm_yday,int(timeofsunmax + 4), int(np.modf(timeofsunmax + 4)[0]*60))
        nsradio = self.datasim.data[(self.datasim.timedata < t1)  | (self.datasim.timedata > t2) ]
        nstemp = self.datasim.tempLL[(self.datasim.timedata < t1)  | (self.datasim.timedata > t2) ]
        ## subtract the mean of the time when no sun is present in the data
        radio = self.datasim.data - np.mean(nsradio)
        temp = self.datasim.tempLL - np.mean(nstemp)
        nstemp = nstemp - np.mean(nstemp)
        ## get the file with temperature fit result
        fitfile = constant.tempfitfolder + '/tempfit_'+nameofstation+ '.npy'
#        fitfile = constant.tempfitfolder + '/tempfit_'+nameoflist[:-4] + '.npy'
        tempfit = np.load(fitfile)
        pfit = np.poly1d(tempfit)
        radio = radio - pfit(temp)
        ## baseline corrected
        nsradioc = nsradio - np.mean(nsradio)    
        nsradioc = nsradioc -  pfit(nstemp)
        self.pointuncert = np.std(nsradioc)
        self.cbaseline = radio

    def getdataforfit(self, signalwindow):
        timeofsunmax = self.simtofmax/100 + 3
        hourarray = utils.gethourarray(self.datasim.timedata)
        fithourarray = hourarray[ np.where( (self.cbaseline< 50) & (hourarray > timeofsunmax -signalwindow) & (hourarray < timeofsunmax + signalwindow ) )]
        fitradio = self.cbaseline[np.where( (self.cbaseline< 50) & (hourarray > timeofsunmax -signalwindow ) & (hourarray < timeofsunmax + signalwindow ) ) ]
        return [fithourarray,fitradio]
        

    # compute the fit of the non sun period to extract the error on each point to be attributed for the sun bump fit
    def geterroronpoint(self, signalwindow):
        timeofsunmax = self.simtofmax/100 + 3
        hourarray = utils.gethourarray(self.datasim.timedata)
#        nsfithourarray = hourarray[ np.where( (hourarray < timeofsunmax - signalwindow) | (hourarray > timeofsunmax + signalwindow ) )]
#        nsfitradio = self.cbaseline[np.where(  (hourarray < timeofsunmax -signalwindow ) | (hourarray > timeofsunmax + signalwindow ) ) ]
#        nsfithourarray = hourarray[ np.where( (self.cbaseline< 50) & (hourarray < timeofsunmax - signalwindow) | (hourarray > timeofsunmax + signalwindow ) )]
#        nsfitradio = self.cbaseline[np.where( (self.cbaseline< 50) & (hourarray < timeofsunmax -signalwindow ) | (hourarray > timeofsunmax + signalwindow ) ) ]
        nsfithourarray = hourarray[ np.where( (self.cbaseline< 50) & (hourarray < timeofsunmax - signalwindow) )]
        nsfitradio = self.cbaseline[np.where( (self.cbaseline< 50) & (hourarray < timeofsunmax - signalwindow) )]
        nsfit = np.polyfit(nsfithourarray,nsfitradio,2)
        blpol = np.poly1d(nsfit)
#        return [nsfithourarray,nsfitradio,blpol(nsfithourarray)]
        return np.std(nsfitradio - blpol(nsfithourarray))


        


    def fitdata(self,signalwindow,method=None):
        timeofsunmax = self.simtofmax/100 +3
        [fithourarray,fitradio] = self.getdataforfit(signalwindow)
        if method == 0 or method == None:
            [popt,pcov] =  utils.fitwithexpo2(fithourarray, fitradio, self.pointuncert, 15, 1.5,timeofsunmax,0,0,0)
            if type(pcov)==type(1.1):
                fittedradio = np.zeros(len(fithourarray))
            else:
                fittedradio = utils.expofunc2(fithourarray,popt[0],popt[1],popt[2],popt[3],popt[4],popt[5])
        if method == 1 :
            [popt,pcov] =  utils.fitwithexpo0(fithourarray, fitradio, self.pointuncert, 15, 1.5,timeofsunmax,0)
            if type(pcov)==type(1.1):
                fittedradio = np.zeros(len(fithourarray))
            else:
                fittedradio = utils.expofunc0(fithourarray,popt[0],popt[1],popt[2],popt[3])
        if np.isinf(pcov).any() or  np.isinf(popt).any():
            print 'ingfffff'
            [popt,pcov] = [np.array([0,0,0,0,0]),np.ndarray(shape=(5,5))]
        if np.isnan(pcov).any() or  np.isnan(popt).any():
            print 'inanana'
            [popt,pcov] = [np.array([0,0,0,0,0]),np.ndarray(shape=(5,5))]
        

        self.fitresult = [popt,pcov]
        return [fithourarray,fittedradio]

    def fitdata2(self,signalwindow):
        timeofsunmax = self.simtofmax/100 +3
        [max,minmax,maxmax] = utils.suntemptoadc(np.array([50,30,120]),self.simmax)
        [fithourarray,fitradio] = self.getdataforfit(signalwindow)
        

        #return max*np.exp(-((x - mu)/sigma)**2) + b*x**2 + c*x + d
        gmodel = Model(utils.expofunc2)
#        gmodel = Model(utils.expofunc0)
        params = Parameters()
        baseline = np.mean(fitradio[10])
        params.add('a', value=max,min=minmax,max=maxmax)
        params.add('mu', value=timeofsunmax)
        params.add('sigma', value=1, min=0.5, max=2)
        params.add('b', value=0)
        params.add('c', value=0)
        params.add('d', value=0)
        result = gmodel.fit(fitradio, x=fithourarray, params=params)
#        result.eval_uncertainty()
#        print(result.fit_report())
        return result


    def isgoodfit(self):
        if  type(self.fitresult[0])==type(1.1):
            self.goodfit = False
            return None
#        timeofsunmax = self.simtofmax/100 +3
        fitres = self.fitresult[0]
        fit_max = fitres[0]
#        print 'fit_max = ', fit_max
        fit_width = fitres[1]
        fit_tofmax = fitres[2]
        deltatofmax = 1
#        good = utils.isgoodfit(fit_max, fit_tofmax,timeofsunmax, deltatofmax, fit_width, 0.5*self.simwidth,1.5*self.simwidth)
#        good = utils.isgoodfit(fit_max, fit_tofmax,timeofsunmax, deltatofmax, fit_width, 0.3, 2)
        good = utils.isgoodfit(fit_max, fit_width, 0.3, 2)
        self.goodfit = good


#     def computetsys(self,exptemp=None):
#         maxfit = self.fitresult[0][0]
#         if exptemp == None:
#             tsys = utils.adctotsys(maxfit,self.simmax)
#         else:
#             tsys = utils.adctotsys(maxfit,exptemp)
#         self.tsys = tsys
        
    def computetsys(self,exptemp=None, maxfit=None):
        if maxfit == None:
            maxfit = self.fitresult[0][0]
        if exptemp == None:
            tsys = utils.adctotsys(maxfit,self.simmax)
        else:
            tsys = utils.adctotsys(maxfit,exptemp)
        self.tsys = tsys
        

    def geterrorsonfit(self):
        perr = np.sqrt(np.diag(self.fitresult[1]))
        erronmax = perr[0]
        erronmax +=0
        erronhmax = perr[2]

        sigdeltaP = erronmax/constant.adctop
        deltaP = self.fitresult[0][0]/constant.adctop
        ln10on10 = np.log(10)/10
        relaeff = 0
        relfsun = 0
        reltsys = np.sqrt(relaeff**2 + relfsun**2 + ( (ln10on10* np.power(10,deltaP/10)) / (np.power(10,deltaP/10) - 1) )**2 *sigdeltaP**2)
#        reltsysstat = np.sqrt( ( (ln10on10* np.power(10,deltaP/10)) / (np.power(10,deltaP/10) - 1) )**2 *sigdeltaP**2)


        self.errortsys = reltsys
        self.errortofmax = erronhmax


    def geterrorsonfit2(self,t):
        pcov = self.fitresult[1]
        perr = np.sqrt(np.diag(pcov))
        popt = self.fitresult[0]
        erronmax = perr[0]
        erronmax +=0
        erronhmax = perr[2]
        x0 = popt[0]
        x1 = popt[1]
        x2 = popt[2]
        x3 = popt[3]
        x4 = popt[4]
        x5 = popt[5]
        dy_dx0 = np.exp(-(t - x2)**2/x1**2) 
        dy_dx1 = x0*np.exp(-(t - x2)**2/x1**2)*(2/x1) 
        dy_dx2 = x0*np.exp(-(t - x2)**2/x1**2)*(2*x2) 
        dy_dx3 =  t**2
        dy_dx4 =  t
        dy_dx5 =  1
        darray = np.array([dy_dx0, dy_dx1, dy_dx2, dy_dx3, dy_dx4, dy_dx5])
        darrayT = np.transpose(darray)
        errsquared = np.dot(darrayT, np.dot(pcov,darray))
        err = np.sqrt(errsquared)
#        print ' !!!!!!!!!!!!!!!! err = ', err 
#        sigdeltaP = erronmax/constant.adctop
        sigdeltaP = err/constant.adctop
        deltaP = self.fitresult[0][0]/constant.adctop
        ln10on10 = np.log(10)/10
        relaeff = 0
        relfsun = 0
        reltsys = np.sqrt(relaeff**2 + relfsun**2 + ( (ln10on10* np.power(10,deltaP/10)) / (np.power(10,deltaP/10) - 1) )**2 *sigdeltaP**2)
#        reltsysstat = np.sqrt( ( (ln10on10* np.power(10,deltaP/10)) / (np.power(10,deltaP/10) - 1) )**2 *sigdeltaP**2)


        self.errortsys = reltsys
        self.errortofmax = erronhmax
        


# #    [popt,pcov] = fitwithexpo2(hourarray, radio, uncert, 15, 1.5,timeofsunmax,0,0,0)
# #    [popt,pcov] = fitwithexpo0(hourarray, radio, uncert, 10, 1.5,timeofsunmax,0)
#     print '[popt,pcov] = ' , popt, ' ', type(pcov)
#     if type(pcov)==type(1.1):
#         continue
#     perr = np.sqrt(np.diag(pcov))
#     erronmax = perr[0]
#     erronhmax = perr[2]
    
#     erronmax += 5
#     erronhmax += 0
#     rfit = utils.expofunc2(fithourarray,popt[0],popt[1],popt[2],popt[3],popt[4],popt[5])
# #    rfit = utils.expofunc0(hourarray,popt[0],popt[1],popt[2],popt[3])
#     goodfit = isgoodfit(stid,popt,timeofsunmax)
#     maxfit = popt[0]
#     adctop = 48.7
#     tsys = maxsim/(np.power(10,maxfit/(10*adctop)) -1)
# ### here
# #    hourarray = hourarray - 3
# #    hourarray = hourarray % 24

#     #    rfit = np.roll(rfit,-sizetoroll)

# #     if goodfit == False:
# #         fig = plt.figure(figsize=(12,6))
# #         fig.suptitle(stname + ' (' + t1.strftime('%d %b %Y')+')',fontweight='bold',fontsize=15)
# #         plt.plot(hourarray,radio,'b.',label='data')
# #         plt.plot(fithourarray,rfit,'r',lw=2,label='fit')
# #         plt.xlabel('local time')
# #         plt.ylabel('corrected baseline [ADC]')
#     if goodfit == True:
# #         fig = plt.figure()
# #         fig.suptitle(stname + ' (' + t1.strftime('%d %b %Y')+')',fontweight='bold',fontsize=15)
# #         plt.plot(hourarray,radio,'b.',label='data')
# #         plt.plot(fithourarray,rfit,'r',lw=2,label='fit')
# #         plt.xlabel('time [UTC]')
#         #         plt.ylabel('corrected baseline [ADC]')
#         datestring = t1.strftime('%d %b %Y')
#         print datestring , ' ', maxfit
#         datearray.append(datestring)
#         adate = np.append(adate,datetime.datetime(t1.year,t1.month,t1.day))
#         asimhmax = np.append(asimhmax,poptsim[2])
#         asimmax = np.append(asimmax, maxsim)
#         aerrmax = np.append(aerrmax,erronmax)
#         aerrhmax = np.append(aerrhmax,erronhmax)
#         tsysall = np.append(tsysall,tsys)
#         #   fig2 = plt.figure(figsize=(12,6))
#         #   plt.plot(time,radio,'b.',label='non selected')
#         #   plt.legend()
#         relaeff = 0
# #        relaeff = relaeffuncert
# #        relfsun = 0.05
#         relfsun = 0.0
#         sigdeltaP = erronmax/adctop
#         deltaP = maxfit/adctop
#         ahmax = np.append(ahmax,popt[2])
#         amax = np.append(amax,popt[0])
#         ln10on10 = np.log(10)/10
#         reltsys = np.sqrt(relaeff**2 + relfsun**2 + ( (ln10on10* np.power(10,deltaP/10)) / (np.power(10,deltaP/10) - 1) )**2 *sigdeltaP**2)
#         reltsysstat = np.sqrt( ( (ln10on10* np.power(10,deltaP/10)) / (np.power(10,deltaP/10) - 1) )**2 *sigdeltaP**2)
#         sigmatsysall = np.append(sigmatsysall,reltsys*tsys)
#         sigmatsysstat = np.append(sigmatsysstat,reltsysstat*tsys)

# ## compute weighted mean and error
# tant = 0
# oneoversigmasquare = 1/(sigmatsysall*sigmatsysall)
# xoversigmasquare = tsysall*oneoversigmasquare
# wmean = np.sum(xoversigmasquare)/np.sum(oneoversigmasquare)
# errorwmean = np.sqrt(1/np.sum(oneoversigmasquare))
# tsys = wmean + tant
# tsysall = tsysall + tant

# print 'final result is ... Tsys = ' , tsys , ' +- ',  errorwmean
# y = np.arange(0,len(tsysall),1)
# x = np.arange(0,len(tsysall),1)
# myticks = datearray
# figres = plt.figure(figsize=(15,5))
# figres.subplots_adjust(left=0.1, bottom=0.3, right=0.94, top=0.9,
#                        wspace=None, hspace=None)
# figres.suptitle(stname,fontsize=15,fontweight='bold')
# #ax = plt.subplot(111)
# theres = (tsys)*np.ones(len(y))
# errtheres = errorwmean*np.ones(len(y))
# ymin = np.min(tsysall-sigmatsysall)
# ymax = np.max(tsysall+sigmatsysall)
# #plt.errorbar(x,tsysall, yerr=sigmatsysall,lw=4, fmt='o',alpha=0.9,label='stat. and sys.')
# plt.errorbar(x,tsysall, yerr=sigmatsysstat,color='b', fmt='o',lw=4, alpha=0.6)
# #plt.errorbar(x,tsysall, yerr=sigmatsysstat,color='b', fmt='o',lw=4, alpha=0.6,label='stat. only')

# plt.xticks(x,myticks,rotation='vertical',size=10)
# plt.fill_between(x, theres-errtheres, theres +  errtheres,facecolor='red',alpha=0.5)
# plt.ylabel('system temperature [K]')
# plt.ylim(ymin,ymax)
# plt.legend()
# #plt.xlim(35,185)
# #plt.ylim(y[0]-0.5,y[-1]+0.5)
# #textstr = '\n $T_{sys}=%.1f \pm%.1f [K]$'%(tsys, errorwmean)
# textstr = '$T_{sys}=%.1f \pm%.1f [K]$'%(tsys, errorwmean)
# #textstr = '$testo$'
# props = dict(boxstyle='round', facecolor='white')
# #plt.gca().text(0.95, 0.9, textstr, transform=plt.gca().transAxes, fontsize=17, fontweight ='bold', verticalalignment='top',horizontalalignment='right', bbox=props)
# plt.gca().text(0.05, 0.9, textstr, transform=plt.gca().transAxes, fontsize=17, fontweight ='bold', verticalalignment='top',horizontalalignment='left', bbox=props)

# #bins = np.linspace(0,300,150)
# #plt.hist(tsysall,bins=bins)

# fighmax = plt.figure(figsize=(15,5))
# #figres.suptitle(stname,fontsize=15,fontweight='bold')
# fighmax.subplots_adjust(left=0.1, bottom=0.3, right=0.94, top=0.9,
#                        wspace=None, hspace=None)
# plt.errorbar(x,ahmax,yerr=aerrhmax, fmt='o',)
# plt.plot(x,asimhmax,lw=2)
# plt.ylabel('time of max [hour]')
# plt.xticks(x,myticks,rotation='vertical',size=10)

# figmax = plt.figure(figsize=(15,5))
# #figres.suptitle(stname,fontsize=15,fontweight='bold')
# figmax.subplots_adjust(left=0.1, bottom=0.3, right=0.94, top=0.9,
#                        wspace=None, hspace=None)
# plt.errorbar(x, amax, yerr=aerrmax,fmt='o',label='data')
# t1 = 30
# t2 = 50
# t3 = 70
# ex1 =adctop*10*np.log10(1+asimmax/t1)
# ex2 =adctop*10*np.log10(1+asimmax/t2)
# ex3 =adctop*10*np.log10(1+asimmax/t3)
# plt.plot(x,ex1,lw=2,label='sim. T_sys = ' +str(t1) + ' K')
# plt.plot(x,ex2,lw=2,label='sim. T_sys = ' +str(t2) + ' K')
# plt.plot(x,ex3,lw=2,label='sim. T_sys = ' +str(t3) + ' K')
# plt.xticks(x,myticks,rotation='vertical',size=10)
# plt.ylabel('radio max [ADC]')
# plt.legend()

# resfile = outf + '/results.txt' 
# fout = open(resfile,'w')
# for i in range(len(tsysall)):    
#     fout.write(str(adate[i].year) + ' ' + str(adate[i].month) + ' ' + str(adate[i].day) + ' ' + str(tsysall[i]) + ' ' + str(sigmatsysall[i])  + ' ' + str(ahmax[i]) + ' ' + str(aerrhmax[i]) + '\n' )

# plt.show()
