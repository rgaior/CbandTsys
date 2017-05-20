#######################################
## make a selection of the day       ##
## usable for the analysis based on  ##
## an iterative fit of the           ##
## temperature dependence            ##
#######################################
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
cwd = os.getcwd()
classpath = cwd + '/../classes/'
utilspath = cwd + '/../utils/'
sys.path.append(utilspath)
sys.path.append(classpath)
import constant
import utils
import pickle
import dataset
import argparse
import scipy.stats as sstat
import datetime
from itertools import compress

############################
##  argument parser       ##
############################
parser = argparse.ArgumentParser()
parser.add_argument("stname", type=str, nargs='?',default='popey', help="station name")
parser.add_argument("-save", help="save if True", action="store_true")
parser.add_argument("-savefit", help="save if True", action="store_true")
args = parser.parse_args()
save = args.save
savefit = args.savefit
st = args.stname
if st == 'all':
    stnames = constant.GDstationidbyname.keys()
else:
    stnames = [st]

firstselected = []

for stname in stnames:
    if stname == 'juan' or stname == 'luis':
        continue
    print stname
    stid = constant.GIGASstationidbyname[stname]

    humidity = np.array([])
    time = np.array([])
    a_radio = np.array([])
    a_temp = np.array([])
    
    nrofday = constant.doy
    a_rms = np.array([])
    a_minmax = np.array([])
    counter = 0
    a_srms = np.array([])
    a_tempsrms = np.array([])
    for y in [2015,2016,2017]:
        for d in range(1,nrofday[y]+1,1):
            ad_srms = np.array([])
            ad_tempsrms = np.array([])
            outfolder = constant.dataresultfolder + str(stid)
            datafilename = outfolder + '/data_' + str(int(y)) + '_' + str(int(d)) + '.pkl'
            if os.path.isfile(datafilename):
                datafile = open(datafilename,'rb')
            else:
                continue
            thedata = pickle.load(datafile)

          #### select the non sun region
            size = len(thedata.data)
            datemiddle = thedata.timedata[int(size/2)]
            day = datemiddle.year
            dsun = datetime.datetime(datemiddle.year, datemiddle.month,datemiddle.day,constant.GDnametom[stname]/100,0,0)
            delta = datetime.timedelta(0.17) #
            radio = thedata.data[ (thedata.timedata < dsun - delta) | (thedata.timedata > dsun + delta) ]
            temp = thedata.tempLL[ (thedata.timedata < dsun - delta) | (thedata.timedata > dsun + delta) ]
            time = thedata.timedata[ (thedata.timedata < dsun - delta) | (thedata.timedata > dsun + delta) ]

        #### humidity selection:
            humsel = 90
            if (thedata.humidity > humsel).any():
                datafile.close()
                continue

        #### nr or point selection:
            nrofpointintrace = 200
            if size < nrofpointintrace:
                datafile.close()
                continue



            minradio = np.min(thedata.data)
            maxradio = np.max(thedata.data)

        #### diff min max selection:
            diffmax = constant.diffmax
            diffmin = constant.diffmin
            if maxradio - minradio > diffmax or maxradio - minradio < diffmin:
                #            fig = plt.figure()
                #            plt.plot(thedata.data)
                datafile.close()
                continue
            a_minmax = np.append(a_minmax,maxradio - minradio)

        #### RMS selection:
            rmsradio = np.std(radio)
            if rmsradio < constant.rmsmin:
                datafile.close()
                continue
            a_rms = np.append(a_rms,rmsradio)
        #### RMS over shorter time period than a day selection:
            nrofpoint = 10
            nrofpointtemp = 10
            itersize = len(radio) -nrofpoint
            for p in range(itersize):
                srms = np.std(radio[p:p+nrofpoint])
                tempsrms = np.std(temp[p:p+nrofpoint])
                a_srms = np.append(a_srms,srms)
                ad_srms = np.append(ad_srms,srms)
                a_tempsrms = np.append(a_tempsrms,tempsrms)
                ad_tempsrms = np.append(ad_tempsrms,tempsrms)
            limsrms = 0.2
            if (ad_srms < limsrms).any():
                datafile.close()
                continue
            if (ad_tempsrms < limsrms/10).any():
                datafile.close()
                continue
            
            cradio = radio - np.mean(radio)
            a_radio = np.append(a_radio, cradio)
            ctemp = temp - np.mean(temp)
            a_temp = np.append(a_temp, ctemp)
            counter += 1
            datafile.close()

#             figadc, (ax0,ax1) = plt.subplots(2,1)
#             figadc.suptitle(stname)
#             ax0.hist(radio - np.mean(radio),bins=100)
#             ax1.plot(time,radio)

            
            firstselected.append(thedata)

###########################
## produce a first fit ####
########################### 
    firstfit = np.polyfit(a_temp,a_radio,1)
    firstcorr = np.poly1d(firstfit)
    xtemp = np.linspace(np.min(a_temp),np.max(a_temp),10)





    print ' counter = ' , counter
    extfile = 'shortrms'
    figcorrel = plt.figure()
    figcorrel.suptitle(stname)
    plt.plot(a_temp, a_radio,'.')
    plt.plot(xtemp,firstcorr(xtemp),'r-',lw=2)
    plt.xlabel('temperature [C]')
    plt.ylabel('radio baseline [ADC]')
    if save:
        outnamecorrel = utils.outname(constant.plotfolder + '/'+ stname  + '_correl_' + extfile,'.png')
        plt.savefig(outnamecorrel+ '.png')
    fighist = plt.figure()
    fighist.suptitle(stname)
    plt.hist(a_rms,bins=100)
    plt.xlabel('Std(radio) [ADC]')
    if save:
        outnamehist = utils.outname(constant.plotfolder + '/'+ stname + '_radiorms_' + extfile,'.png')
        plt.savefig(outnamehist+ '.png')
    figminmax = plt.figure()
    figminmax.suptitle(stname)
    plt.hist(a_minmax,bins=100)
    plt.xlabel('max - min radio [ADC]')
    if save:
        outnameminmax = utils.outname(constant.plotfolder + '/'+ stname + '_minmax_' + extfile,'.png')
        plt.savefig(outnameminmax+ '.png')
#     figadc = plt.figure()
#     figadc.suptitle(stname)
#     plt.hist(a_radio,bins=100)
#     plt.xlabel('radio values [ADC]')
#     if save:
#         outradioval = utils.outname(constant.plotfolder + '/'+ stname + '_val_' + extfile,'.png')
#         plt.savefig(outradioval+ '.png')


##################################
## second round of selection  ####
## iterative fitting          ####
##################################
limrms = 100 # limit rms to begin with
finallimrms = constant.finallimrms # target final rms
isgood = False
count = 0
selected = firstselected
fit = firstfit
fitcorr = firstcorr
while isgood == False:
    count+=1
#    print 'count in while = ', count
    if count > 100:
        isgood = True
        continue
    a_corrrms = np.array([])
    a_condition = np.array([])
    a_radio = np.array([])
    a_temp = np.array([])
    fil = []
    for s in selected:
        size = len(s.data)
        datemiddle = s.timedata[int(size/2)]
        day = datemiddle.year
        dsun = datetime.datetime(datemiddle.year, datemiddle.month,datemiddle.day,constant.GDnametom[stname]/100,0,0)
        delta = datetime.timedelta(0.17) 
        radio = s.data[ (s.timedata < dsun - delta) | (s.timedata > dsun + delta) ]
        temp = s.tempLL[ (s.timedata < dsun - delta) | (s.timedata > dsun + delta) ]
        time = s.timedata[ (s.timedata < dsun - delta) | (s.timedata > dsun + delta) ]
        radio = radio - np.mean(radio)
        temp = temp - np.mean(temp)
        corr_radio = radio - fitcorr(temp)
        corrrms =  np.std(corr_radio) 
        a_corrrms = np.append(a_corrrms,corrrms)            
        if corrrms < limrms:
            fil.append(True) 
            a_radio = np.append(a_radio, radio)
            a_temp = np.append(a_temp, temp)
        else:
            fil.append(False)
    if np.max(a_corrrms) < finallimrms:
        print 'np.max(a_corrrms) = ' , np.max(a_corrrms)
        isgood = True
    else:
        limrms = np.max(a_corrrms)
        

    selected = list(compress(selected, fil))
    fit = np.polyfit(a_temp,a_radio,1)
    fitcorr = np.poly1d(fit)

figcorrrms = plt.figure()
figcorrrms.suptitle(stname)
plt.hist(a_corrrms,bins=50)
plt.xlabel('rms (after corr) [ADC]')
if save:
    outnamecorrrms = utils.outname(constant.plotfolder + '/'+ stname + '_corrrms_' + extfile,'.png')
    plt.savefig(outnamecorrrms+ '.png')

figlastcorrel = plt.figure()
figlastcorrel.suptitle(stname)
plt.plot(a_temp,a_radio,'.')
x = np.linspace(np.min(a_temp),np.max(a_temp),10)
plt.plot(x, fitcorr(x),'r-',lw=2)
plt.xlabel('temperature [C]')
plt.ylabel('radio [ADC]')
print 'kept number of trace = ', len(selected) ,' len(firstselected) = ' , len(firstselected)

outlistname = constant.listfolder + 'newlist_' + stname + '.txt'
f = open(outlistname,'w')
for s in selected:
    figt = plt.figure()
    figt.suptitle(s.timedata[100])
    plt.plot(s.timedata,s.data)
    (year,day) = utils.datetodoy(s.timedata[100])
#    print 'year = ' ,year, ' day = ' , day
    f.write(str(year) + ' ' + str(day) + '\n' )

[fit,cov] = np.polyfit(a_temp,a_radio,1,cov=True)
pfit = np.poly1d(fit)
print fit, ' ' , np.sqrt(np.diag(cov))
if savefit:
    outfilefit = constant.tempfitfolder + '/tempfit_'+stname 
    print outfilefit
    np.save(outfilefit,fit)

print fit
plt.show()
