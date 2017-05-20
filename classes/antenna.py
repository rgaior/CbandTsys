import math
import numpy as np
from numpy.linalg import inv
import os
import sys
cwd = os.getcwd()
utilspath = cwd + '/../utils/'
sys.path.append(utilspath)
import utils
import constant
gainfiledmx = constant.gainfiledmx
gainfilenorsat = constant.gainfilenorsat
gainfilenorsat2 = constant.gainfilenorsat2
gainfilehelix = constant.gainfilehelix

class Antenna:
    def __init__(self, type, name = None, freq=None, newtheta=0, newphi=0):
        self.type = type
        self.pattern = {}
        self.antennageo = ()
        self.rotationmatrix = np.array([])
        self.name = name
        self.deltaphi = 0
        self.deltathteta = 0
        self.newtheta = newtheta
        self.newphi = newphi
        if self.type.lower() == 'dmx' or 'dmx_meas':
            self.deltaphi = 1
            self.deltatheta = 10
            self.fc = 3.8e9
            if freq == None:
                self.loadgain(3.8)
            else:
                self.loadgain(freq)

        if self.type.lower() == 'norsat':
            self.deltaphi = 0.5
            self.deltatheta = 0.5
            self.fc = 3.8e9
            if self.newtheta != 0 or self.newphi !=0:
                self.antennageo = (newtheta,newphi)
            else:
                self.antennageo = constant.GDantennageo[self.name]
            self.setrotationmatrix()
            self.loadgain()
        if self.type.lower() == 'helix':
            self.deltaphi = 2
            self.deltatheta = 2
            self.loadgain()
            self.antennageo = constant.Helixantennageo[self.name]
            self.setrotationmatrix()
            self.fc = 1.2e9

        
    def loadgain(self,freq=None):
        if self.type.lower() == 'dmx':
#            self.pattern = utils.getpatterntuplefreq(constant.gainfiledmx2,freq)
            self.pattern = utils.getpatterntuple(constant.gainfiledmx)
        if self.type.lower() == 'dmx_meas':
            self.pattern = utils.getpatterntuplefreq(constant.gainfiledmx2,freq)
#            print self.pattern
        if self.type.lower() == 'norsat':
#            self.pattern = utils.getpatterntuple(gainfilenorsat)
            self.pattern = utils.getpatterntuplefromnpy(constant.gainfilenorsat2)
        if self.type.lower() == 'helix':
            self.pattern = utils.getpatterntuple(constant.gainfilehelix)

    def getphiangle(self):
        return self.antennageo[1]
    def getthetaangle(self):
        return self.antennageo[0]
            
    def setrotationmatrix(self):
        rotthetaaxis = np.array([0,1,0])
        rotphiaxis = np.array([0,0,1])
        rottheta = self.antennageo[0]
        rotphi = self.antennageo[1]
        rotthetaangle = utils.degtorad(rottheta)
        rotphiangle = utils.degtorad(rotphi)
        rotthetamatrix = utils.rotation_matrix(rotthetaaxis, -rotthetaangle)
        rotphimatrix = utils.rotation_matrix(rotphiaxis, -rotphiangle)
        rottot = np.dot(rotthetamatrix,rotphimatrix)
        self.rotationmatrix = rottot

        
    def gettheta(self):
        if self.name == None:
            return 0
        angles = rotation[self.name]
        return angles[0]
    def getphi(self):
        if self.name == None:
            return 0
        angles = rotation[self.name]
        return angles[1]
        
    def getpatt(self):
        theta = np.array([])
        phi = np.array([])
        gain = np.array([])
        for p in self.pattern:
            theta = np.append(theta,p[0])
            phi = np.append(phi,p[1])
            gain = np.append(gain,self.pattern[p])
        return [theta,phi,gain]

    def interpolatepattern(self):
        patt = self.getpatt()
        theta = patt[0]
        phi = patt[1]
        gain = patt[2]
        mintheta = np.min(theta)
        minphi = np.min(phi)
        maxtheta = np.max(theta)
        maxphi = np.max(phi)
        newtheta = np.arange(mintheta,maxtheta,self.deltatheta)
        newphi = np.arange(minphi,maxphi,self.deltaphi)
        newpatt = utils.interpolatepattern(theta,phi,gain,newtheta,newphi)
        self.pattern = newpatt

    def getinterpolatepattern(self,deltatheta, deltaphi):
        patt = self.getpatt()
        theta = patt[0]
        phi = patt[1]
        gain = patt[2]
        mintheta = np.min(theta)
        minphi = np.min(phi)
        maxtheta = np.max(theta)
        maxphi = np.max(phi)
        newtheta = np.arange(mintheta,maxtheta,deltatheta)
        newphi = np.arange(minphi,maxphi,deltaphi)
        newpatt = utils.interpolatepattern(theta,phi,gain,newtheta,newphi)
        return newpatt
    
    def getgainnormal(self,theta,phi):
        thetaphi = utils.getclosesttuple(theta,phi,self.deltatheta,self.deltaphi)
        if thetaphi in self.pattern:
            gain = self.pattern[thetaphi]
        else:
            theta = utils.format(thetaphi[0])
            phi = utils.format(thetaphi[1] % 180)
            gain = self.pattern[(theta,phi)]
        return gain

    def getgainonephi(self,theta,phi):
        #thetaphi = (theta,phi)
        thetaphi = utils.getclosesttuple(theta,0.0,self.deltatheta,self.deltaphi)
        if thetaphi in self.pattern:
            gain = self.pattern[thetaphi]
        else:
            print 'not in pattern ', thetaphi
            theta = utils.format(thetaphi[0])
            gain = self.pattern[(theta,0.0)]
        return gain
        
    def getgain(self,theta,phi):
        if self.type.lower() == 'dmx' or 'dmx_meas':
            gain = self.getgainonephi(theta,phi)
        if self.type.lower() == 'norsat':
            gain = self.getgainnormal(theta,phi)
        if self.type.lower() == 'helix':
            gain = self.getgainnormal(theta,phi)
        return gain

    def getaeff(self,theta,phi):
        gain = self.getgain(theta,phi)
        gainlin = utils.dbtolin(gain)
        return utils.gaintoaeff(self.fc, gainlin)
