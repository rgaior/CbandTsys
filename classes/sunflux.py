import utils
import constant
import math
import numpy as np
#f107file = '/Users/romain/work/Auger/EASIER/LPSC/suntransit/data/sunflux2014daily.dat'
#posfile = '/Users/romain/work/Auger/EASIER/LPSC/suntransit/data/AnnualSunPath_2014_Malargue_spa.txt'
posfile = '/Users/romain/work/Auger/EASIER/LPSC/suntransit/data/AnnualSunPath_2011to2017.txt'
#posfile = '/Users/romain/work/Auger/EASIER/LPSC/codecorinne/myspa/input/AnnualSunPath_2014_Malargue_spa.txt'
class Sunflux:
    def __init__(self, frequency = 3.8):
        #f107 vs time
        self.f107 = {}
        self.frequency = frequency
        self.qs = 0
        self.vs = {}
        self.flux = {}
        self.position = {}
        
        
    def setfluxes(self, type=None):
        if type==None or type == 'canadian':
            if type == None:
                self.loadf107()
            elif type == 'canadian':
                self.loadf107('canadian')
            self.setquietsunvalue()
            self.setvaryingsun()
            self.settotalflux()
        if type == 'nobeyama':
            self.loadnobeyama()

    def loadnobeyama(self, type = None):
        if self.frequency == 3.8:
            fluxfile = constant.nobeyamafile
        elif self.frequency == 1.2:
            fluxfile = constant.nobeyamafileL
        self.flux = utils.getfluxtuplefromnobeyama(fluxfile)

    def loadf107(self, type = None):
        if type == None:
            f107file = constant.f107fileUS
            self.f107 = utils.getf107tuple(f107file)
        elif type == 'canadian':
            f107file = constant.f107fileCanada
            self.f107 = utils.getf107tuplefromcanadian(f107file)
            
    def getf107(self,year,doy):
        yeardoy = (year,doy)
        if yeardoy in self.f107:
            flux = self.f107[yeardoy]
            return flux
        else:
            return 0

    def getvs(self,year,doy):
        yeardoy = (year,doy)
        flux = self.vs[yeardoy]
        return flux

    def getflux(self,year,doy,whatflux =None):
        yeardoy = (year,doy)
        if not self.f107.keys():
            if yeardoy in self.flux:
                return self.flux[yeardoy]
            else:
                return 0
        elif (yeardoy in self.f107.keys()):
            if whatflux == None or whatflux.lower() == 'total':
                return self.vs[yeardoy] + self.qs 
            if whatflux.lower() == 'quiet' or 'quiet' in whatflux.lower():
                return self.qs
            if whatflux.lower() == 'f107' or '107' in whatflux.lower():
                return self.f107[yeardoy]
        else:
            return 0
    def setquietsunvalue(self):
        quietsun = 26.4 + 12.4*self.frequency + 1.11*self.frequency**2
        self.qs = quietsun
        
    def setvaryingsun(self):
        vs = {}
        for k,v in zip(self.f107.keys(),self.f107.values()) :
            date = k
            varyingcompo = (0.64*(v-70)*np.power(self.frequency,0.4))/(1 + 1.56*(np.log(self.frequency/2.9))**2)
            vs[date] = varyingcompo
        self.vs = vs

    def settotalflux(self):
#        if not self.f107.keys():
        flux = {}
        for date,f in zip(self.vs.keys(),self.vs.values()):
            theflux = f + self.qs
            flux[date] = theflux
        self.flux = flux

    def setposition(self):
        self.position = utils.getpositiontuple(posfile)
        
    def getposition(self,year, doy):
        return self.position[(year,doy)]

