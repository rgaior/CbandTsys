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
    goodlistname = stname + '.txt'
goodlistname = stname + '.txt'
[goodyear,goodday] = utils.getdaysfromlist(constant.listfolder + goodlistname)

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
folder =  constant.simresultfolder

if detector == 'norsat':
    centertheta =  constant.GDantennageo[stname][0]
    centerphi =  constant.GDantennageo[stname][1]
elif detector == 'helix':
    centertheta =  constant.Helixantennageo[stname][0]
    centerphi =  constant.Helixantennageo[stname][1]
#start = ttime.time()
#end = ttime.time()
#print(end - start)

ant = antenna.Antenna(detector,stname,newtheta=0,newphi=0)
deltathetas = range(-30,30,1)
deltaphis = range(-30,30,1)

for delt in deltathetas:
    newt = centertheta + delt
    for delp in deltaphis:
        newp = centerphi + delp
        befantsetup = ttime.time()
        ant.antennageo = (delt,delp)
        ant.setrotationmatrix
        afterantsetup = ttime.time()
#        print 'ant setup =  ', afterantsetup - befantsetup
        print ant.antennageo
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
                beftransfo = ttime.time()
                newpos = utils.transformsunpos(pos[0],pos[1])
                newpos = utils.transformtrajectory(newpos[0],newpos[1],ant.rotationmatrix)
                aftertransfo = ttime.time()
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
                hourarray = np.append(hourarray,time.hour)
                dateutc = utils.datettotimestamp(time) + 3*60*60
                timeutc = utils.tstamptodatetime(dateutc)
#                yeardate = np.append(yeardate,timeutc)
                temp = polfactor*utils.sfutoSI(totsunflux)*aeff/1.38e-23
#                yeartemp = np.append(yeartemp,temp)
                daytemp = np.append(daytemp,temp)
            if detector == 'norsat':
                filename = folder + str(constant.GDstationidbyname[stname]) + '/exptemp_' + stname + '_' + str(delt) + '_' + str(delp) + '_' + str(y) + '_' + str(d) + '.txt'
#                print filename

            elif detector == 'helix':
                filename = folder + str(constant.Helixstationidbyname[stname]) + '/exptemp_' + stname + '_' + str(delt) + '_' + str(delp) + '_' + str(y) + '_' + str(d) + '.txt'
            f = open(filename,'w')
#            befwriting = ttime.time()
            for t,temp  in zip(timearray,daytemp):
                f.write(str(t.hour) +  ' ' + str(t.minute) + ' ' + str(temp) + '\n') 
#            afterwriting = ttime.time()
#            print ' writing = ' , afterwriting - befwriting
            f.close()
