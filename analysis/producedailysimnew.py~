###########################################
## produce python type files             ##
###########################################
import numpy as np
import sys
import os
cwd = os.getcwd()
classpath = cwd + '/../classes/'
utilspath = cwd + '/../utils/'
sys.path.append(utilspath)
sys.path.append(classpath)
import constant
import utils
import datetime
import dataset
import antenna
import sunflux
import argparse
import time as ttime


############################
##  argument parser       ##
############################
parser = argparse.ArgumentParser()
parser.add_argument("stname", type=str, nargs='?',default='popey', help="station name")
parser.add_argument("-list", type=str, help="list of good days")
parser.add_argument("--theta", type=int, default=0, help="deviation from nominal position in zenith")
parser.add_argument("--phi", type=int, default=0,help="deviation from nominal position in azimuth")

args = parser.parse_args()
stname = args.stname
theta = args.theta
phi = args.phi
stid = constant.GDstationidbyname[stname]
if args.list:
    listfile = args.list
    goodlistname = listfile
else:
    goodlistname = 'newlist_' +  stname + '.txt'
[goodyear,goodday] = utils.getdaysfromlist(constant.listfolder + goodlistname)
print 'list = ', goodlistname

detector = 'norsat'
#ant = antenna.Antenna(detector,stname)
frequency = 3.8
if detector == 'dmx' or detector == 'norsat':
    frequency = 3.8 # GHz
if detector == 'helix':
    frequency = 1.2 # GHz
sflux = sunflux.Sunflux(frequency = frequency)
sflux.setfluxes('nobeyama')
sflux.setposition()

#for doy in range(1,100,10):
#yeartemp = np.array([])
#yeardate = np.array([])
polfactor = 0.5
amax = np.array([])
a_date = np.array([])
atmax = np.array([])
hhmm = np.array([])
nrofday = constant.doy
folder =  constant.mainfolder + '/simulation/'

if detector == 'norsat':
    centertheta =  constant.GDantennageo[stname][0]
    centerphi =  constant.GDantennageo[stname][1]
elif detector == 'helix':
    centertheta =  constant.Helixantennageo[stname][0]
    centerphi =  constant.Helixantennageo[stname][1]
#start = ttime.time()
#end = ttime.time()
#print(end - start)
pi = np.pi

ant = antenna.Antenna(detector,stname,newtheta=0,newphi=0)
deltmax = 50
deltathetas = range(0,deltmax + 1,1)
nrofpointmax = 20
step = 2*pi*deltmax/nrofpointmax

for delt in deltathetas:
    nrofpoint = 2*pi*delt/step
    deltaphis = np.linspace(-180,180,int(nrofpoint))
    deltaphis = deltaphis.astype(int)
    for delp in deltaphis:
        fname = folder + str(constant.GDstationidbyname[stname]) + '/exptemp_' + stname + '_' + str(delt) + '_' + str(delp) + '.txt'
        if os.path.isfile(fname):
            print ' already exist ! '
            continue
        newt = centertheta + delt*np.cos(delp*pi/180)
        newp = centerphi + delt*np.sin(delp*pi/180)
        ant.antennageo = (newt,newp)
        #        ant.antennageo = (delt,delp)
        ant.setrotationmatrix()
#        afterantsetup = ttime.time()
#        print 'ant setup =  ', afterantsetup - befantsetup

        print ant.antennageo
        if detector == 'norsat':
            filename = folder + str(constant.GDstationidbyname[stname]) + '/exptemp_' + stname + '_' + str(delt) + '_' + str(delp) + '.txt'
        elif detector == 'helix':
            filename = folder + str(constant.Helixstationidbyname[stname]) + '/exptemp_' + stname + '_' + str(delt) + '_' + str(delp) + '.txt'
        f = open(filename,'w')
        for y,d in zip(goodyear,goodday):
            y = int(y)
            d = int(d)
            date = utils.doytodate(y,d)
            totsunflux = sflux.getflux(y,d)
            pos = sflux.getposition(y,d)
            sec = np.linspace(0,24*60*60,len(pos[0]))
            posplot = utils.transformsunpos(pos[0],pos[1])
            if detector=='dmx':
                newpos = utils.transformsunposdmx(pos[0],pos[1])
            else:
#                beftransfo = ttime.time()
                newpos = utils.transformsunpos(pos[0],pos[1])
                newpos = utils.transformtrajectory(newpos[0],newpos[1],ant.rotationmatrix)
#                aftertransfo = ttime.time()
#                print 'transfi =  ', aftertransfo - beftransfo
            max = -10
            daytemp = np.array([])
            hourarray = np.array([])
            timearray = np.array([])
            for t,p,s in zip(newpos[0],newpos[1],sec):
                aeff = ant.getaeff(t,p)
                [h,m,s] = utils.secondinday(s)
                time = datetime.datetime(date.year,date.month,date.day,h,m,s)
                timearray = np.append(timearray,time)
                hourarray = np.append(hourarray,time.hour + float(time.minute)/60)
#                print hourarray
                dateutc = utils.datettotimestamp(time) + 3*60*60
                timeutc = utils.tstamptodatetime(dateutc)
#                yeardate = np.append(yeardate,timeutc)
                temp = polfactor*utils.sfutoSI(totsunflux)*aeff/1.38e-23
#                yeartemp = np.append(yeartemp,temp)
                daytemp = np.append(daytemp,temp)
            # fit the temp profile:
            simtofmax = hourarray[np.argmax(daytemp)]
            max = np.max(daytemp)
            width = 1.5
            [poptsim,pcovsim] = utils.fitwithexpo0noerr(hourarray, daytemp, max, width,simtofmax,0)
#            print 'poptsim = ' , poptsim
            if type(poptsim) == type(1.00):
                f.write(str(y) + ' ' + str(d) + ' ' + str(0) + ' '+ str(0) + ' '+ str(0) + ' '+ str(0) + '\n') 
            else:
                f.write(str(y) + ' ' + str(d) + ' ' + str(poptsim[0]) + ' '+ str(poptsim[1]) + ' '+ str(poptsim[2]) + ' '+ str(poptsim[3]) + '\n') 
# #           
# #            befwriting = ttime.time()
#             for t,temp  in zip(timearray,daytemp):
#              afterwriting = ttime.time()
# #            print ' writing = ' , afterwriting - befwriting
        f.close()
