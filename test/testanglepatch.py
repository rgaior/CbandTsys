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

args = parser.parse_args()
stname = args.stname
stid = constant.GDstationidbyname[stname]


detector = 'norsat'
#ant = antenna.Antenna(detector,stname)
frequency = 3.8
if detector == 'dmx' or detector == 'norsat':
    frequency = 3.8 # GHz
if detector == 'helix':
    frequency = 1.2 # GHz

if detector == 'norsat':
    centertheta =  constant.GDantennageo[stname][0]
    centerphi =  constant.GDantennageo[stname][1]
elif detector == 'helix':
    centertheta =  constant.Helixantennageo[stname][0]
    centerphi =  constant.Helixantennageo[stname][1]

ant = antenna.Antenna(detector,stname,newtheta=0,newphi=0)
deltathetas = range(0,15,1)
k = 180
pi = np.pi
radspace = 2*pi/k

for delt in deltathetas:
    newt = centertheta + delt
    rayon = np.abs(2*pi*np.sin(newt*pi/180))
    steps = int(rayon/radspace) + 1
    deltaphis = np.linspace(-30,30,steps)    
    deltaphis = deltaphis.astype(int)
    deltaphis = np.unique(deltaphis)
    for delp in deltaphis:
        newp = centerphi + delp
        #        befantsetup = ttime.time()
        ant.antennageo = (newt,newp)
#        ant.antennageo = (delt,delp)
        ant.setrotationmatrix()
#        afterantsetup = ttime.time()
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
