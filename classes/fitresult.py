import os
import sys
cwd = os.getcwd()
utilspath = cwd + '/../utils/'
sys.path.append(utilspath)
import utils
import constant

class Fitresult:
    def __init__(self,filename = '', newtheta=0, newphi=0):
        self.filename = filename
        self.modelname = ''
        self.funceval = 0 
        self.datapoints = 0 
        self.variables = 0
        self.chi2 = 0
        self.redchi2 = 0
        self.a = 0
        self.erra = 0
        self.mu =0 
        self.errmu =0 
        self.sigma =0 
        self.errsigma =0 
        self.b = 0 
        self.errb = 0 
        self.c = 0 
        self.errc = 0 
        self.d = 0
        self.errd = 0

    def fill(self):
        [self.modelname,self.funceval,self.datapoints,self.variables,self.chi2,self.redchi2,self.a,self.erra,self.mu,self.errmu,self.sigma,self.errsigma,self.b,self.errb,self.c,self.errc,self.d,self.errd] = utils.readfitfile(self.filename)
        
