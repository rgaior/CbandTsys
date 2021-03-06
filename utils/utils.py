import numpy as np
import pickle
import scipy.signal as signal
import math
import sys
import os
cwd = os.getcwd()
utilspath = cwd + '/utils/'
sys.path.append(utilspath)
import constant
###################################
### data loading/reading ##########
###################################
import ROOT as r
from root_numpy import root2rec
def loaddata(filename):
    a = root2rec(filename)
    return a

def loadparams(filename):
    fin = open(filename,'r')
    params = {}
    for l in fin:
        par =  np.asarray(l.split()[4:],dtype=float)
        stnr = int(l.split()[1])
        params[stnr] = par
    return params

def readtempfile(filename):
    f = open(filename,'r')
    hour = np.array([])
    min = np.array([])
    temp = np.array([])
    for l in f:
        lsplit = l.split()
        hour = np.append(hour,float(lsplit[0]))
        min = np.append(min,float(lsplit[1]))
        temp = np.append(temp,float(lsplit[2]))
    return [hour,min,temp]

def getdaysfromlist(filename):
    f = open(filename,'r')
    year = np.array([])
    day = np.array([])
    for l in f:
        lsplit = l.split()
        year = np.append(year,int(lsplit[0]))
        day = np.append(day,int(lsplit[1]))
    return [year,day]

def makeprofile(x,y,nrofbins,xmin,xmax):
#    from root_numpy import fill_profile
    p = r.TProfile("test","test",int(nrofbins),float(xmin),float(xmax))
#    p = r.TProfile(xmin,xmax)
    for xel,yel in zip(x,y):
        p.Fill(xel,yel)
        
    xout = np.array([])
    yout = np.array([])
    erryout = np.array([])
    errxout = np.array([])
    binsize = float((xmax-xmin))/nrofbins
    for ibin in range(1,nrofbins+1,1):
        ix = xmin + (ibin-1 + 0.5)*binsize
        xout = np.append(xout,ix)
        iy = p.GetBinContent(ibin)
        yout = np.append(yout,iy)
        ierr = p.GetBinError(ibin)
        erryout = np.append(erryout,ierr)
        errxout = np.append(errxout,binsize/2)
    return [xout,yout,errxout,erryout]


def readtwocolfile(file):
    f = open(file,'r')
    t = np.array([])
    controlperiod = np.array([])
    for l in f:
        t = np.append(t,float(l.split()[0]))
        controlperiod = np.append(controlperiod,int(l.split()[1]))
    f.close()
    return [t,controlperiod]


def outname(base,extension):
    i = 0
    while os.path.exists(base+ '%s' % i + extension):
        i += 1
    return base + str(i)


##################################
### conversion function ##########
##################################
from datetime import date
import datetime
def gpstodate(gpssecond):
    return  date.fromtimestamp(gpssecond+315964800)
import datetime
def gpstodatetime(gpssecond):
    return  datetime.datetime.fromtimestamp(gpssecond+315964800)

def tstamptodatetime(tstamp):
    return  datetime.datetime.utcfromtimestamp(tstamp)
def nptstamptodatetime(tstamp):
    date = np.array([])
    for t in tstamp:
        d = tstamptodatetime(t)
        date = np.append(date,d)
#        print t, ' ' , d
    return  date
 
def datettotimestamp(dt):
    if not isinstance(dt, datetime.date):
        print 'you should give a datetime.date or datetime.datetime instance in argument'
        return 
    elif not isinstance(dt, datetime.datetime):
        dt = datetime.datetime(dt.year,dt.month,dt.day) 
    timestamp = (dt - datetime.datetime(1970, 1, 1)).total_seconds()
    return timestamp
    
def datestringtodate(date):
#    print date[:4]
    y = int(date[:4])
    m = int(date[4:6])
    d = int(date[6:8])
    print 'y = ' ,y, ' m = ', m , ' d = ',d
    thedate = datetime.date(y,m,d)
    return thedate



def doytodate(year,doy,hour=None,minute=None):
    if hour == None and minute == None:
        date = datetime.datetime.strptime(str(year)+ ' '+str(doy), '%Y %j')
    elif minute == None:
        date = datetime.datetime.strptime(str(year)+ ' '+str(doy) + ' '+str(hour), '%Y %j %H')
    else:
        date = datetime.datetime.strptime(str(year)+ ' '+str(doy) + ' '+str(hour)+ ' ' +str(minute) , '%Y %j %H %M')
    return date
    
def datetodoy(date):
    year = date.year
    day = int(date.strftime('%j'))
    return (year,day)

def doytoUTC(year,doy,hour=None,minute=None):
    date = doytodate(year,doy,hour,minute)
    tstamp = datettotimestamp(date)
    return tstamp

def UTCtodoy(utc):
    date = tstamptodatetime(utc)
    return datetodoy(date)

def hhmmtosecond(hhmm):
    hh = hhmm/100
    mm = hhmm % 100
    sec = hh*3600 + mm*60
    return sec

def sectohhmm(sec):
    h = int(sec/3600)
    m = int(sec%3600)
    hhmm = h*100+m
    return hhmm

def hhmmtohour(hhmm):
    hh = hhmm/100
    mm = hhmm % 100
    sec = hh*3600 + mm*60
    h = hh + mm.astype(float)/60
    return h

def hourtohhmm(hours):
    hh = hours/100
    hh = hh.astype(int)
    mm = (hours-hh*100)*0.6
    hhmm = hh*100 + mm
    return hhmm

def timetohour(hour,min):
    return hour + float(min)/60.


###########################################
####   data selection/correction      #####
###########################################

def correctwithfct(data, x, function):
#    print function
    newdata = data - function(x)
    return newdata

def correctwithpoly(data,x,poly):
#    print function
    newdata = data - poly(x)
    return newdata

def kinkfcn(params, x, data):                                                                            
    a1 = params['a1'].value 
    b1 = params['b1'].value                                                                    
    a2 = params['a2'].value
    b2 = params['b2'].value
    t = params['t'].value
    x1 = x[x<t]
    x2 = x[x>=t]
    y1 = a1*x1 + b1
    y2 = a2*x2 + b2
    model = np.array([])
    model = np.append(model,y1)
    model = np.append(model,y2)
    return model - data
###############################################
####              filtering               #####
###############################################

def lowpass(amp, sampling, order, fcut):
    Nyfreq = sampling/2
    ratiofcut = float(fcut)/Nyfreq
    b, a = signal.butter(order, ratiofcut, 'low')
    filtered = signal.filtfilt(b, a, amp)
    return filtered

def lowpasshard(amp, sampling, fcut):
    fft = np.fft.rfft(amp)
    freq = np.fft.rfftfreq(len(fft),float(1./sampling))
    Nyfreq = sampling/2
    #    print 'Nyfreq = ' , Nyfreq, 'fcut = ', fcut
    min = np.min(np.absolute(fft))
    ratiofcut = float(fcut)/float(Nyfreq)
    size = len(fft)
    newpass = fft[:int(ratiofcut*size)]
    sizeofzeros = size - len(newpass)
    newcut = np.zeros(sizeofzeros)
    newfft = np.append(newpass,newcut)
    out = np.fft.irfft(newfft)
    return out.real

def highpass(amp, sampling, order, fcut):
    Nyfreq = sampling/2
    ratiofcut = float(fcut)/Nyfreq
    b, a = signal.butter(order, ratiofcut, 'high')
    filtered = signal.filtfilt(b, a, amp)
    return filtered

def highpasshard(amp, sampling, fcut):
    fft = np.fft.rfft(amp)
    freq = np.fft.rfftfreq(len(fft),float(1./sampling))
    Nyfreq = sampling/2
    min = np.min(np.absolute(fft))
    ratiofcut = float(fcut)/Nyfreq
    size = len(fft)
    newpass = fft[int(ratiofcut*size):]
    sizeofzeros = size - len(newpass)
    newcut = np.zeros(sizeofzeros)
    newfft = np.append(newpass,newcut)
    out = np.fft.irfft(newfft)
    return out.real


def slidingwindow(y,bins,option=None):
    window = np.ones(bins)/bins
    if option is not None:
        if option.lower() not in ['full','same','valid']:
            print 'invalid option, check your sliding window'
    if option == None:
        return np.convolve(y,window,'same')
    else:
        return np.convolve(y,window,option)

def matchedfilter(y,sig,option=None):
    filtered = signal.correlate(y,sig, mode='full')
#    filtered = signal.correlate(y,sig, mode='valid')
    return filtered


def getxforconv(x,size):
    diff = len(x) - size
    if (diff==0):
        return x
    else:
        return x[diff/2:-diff/2]


def gauss(x,a,b,c):
    g = a*np.exp( -((x-b)**2)/(2*c**2) )
    return g

def issimilarfit(fit1,fit2,tol):
    sim = True
    for f1,f2 in zip(fit1,fit2):
        if f2 > (1+tol)*f1 or f2 < (1-tol)*f1:
            sim = False
    return sim

##############################
## sun transit function   ####
##############################
import pickle
def getsunmax(date):
    sundatafile = '/Users/romain/work/Auger/EASIER/LPSC/monitoring/data/sundata/sundata.pkl'
    pkl_file = open(sundatafile, 'rb')
    sunflux = pickle.load(pkl_file)
    pkl_file.close()
    flux = sunflux[date]
    print 'flux = ', flux
    return flux

def correctmonit(baseline):
    amp_v = np.array([])
    for amp in baseline:
        if amp < 200:
            amp = amp + 655
        amp_v = np.append(amp_v,amp)
    return amp_v
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def suntemptoadc(tsys,temp):
    adc =10*np.log10( (tsys+temp)/tsys )*constant.adctop
    return adc 

def adctotsys(adc,temp):
    adctodb = constant.adctop
    tsys = temp/( np.power(10, adc/(adctodb*10)) - 1 )
    return tsys

def expofunc0(x, a, sigma,mu,c):
    return a*np.exp(-((x - mu)/sigma)**2) + c

def expofunc1(x, a, sigma,mu,b,c):
    return a*np.exp(-((x - mu)/sigma)**2) + b*x + c

def expofunc(x, a, sigma,mu,b,c):
    return a*np.exp(-((x - mu)/sigma)**2) + b*x + c

def expofunc2(x, a, sigma,mu,b,c, d):
    return a*np.exp(-((x - mu)/sigma)**2) + b*x**2 + c*x + d

def expofunctwolinear(x, a, sigma, mu, p00, p01, p10, p11):
    hmax = 1700
    res = np.array([])
    res = a*np.exp(-((x[x<hmax] - mu)/sigma)**2) + p00 + p01*x[x<hmax]
    res = np.append(res,a*np.exp(-((x[x>=hmax] - mu)/sigma)**2) + p10 + p11*x[x>=hmax])
    return res
        

def getexpectedtemp(file):
    #    file format: y m d maxadc
    f = open(file,'r')
    day = {}
    for l in f:
        ls = l.split()
        d = (int(ls[0]),int(ls[1]),int(ls[2]))
        temp = float(ls[3])
        day[d] = temp
    return day


def checkfit(file, tol, date,timeofmax,width):
    f = open(file,'rb')
    dict = pickle.load(f)
    timeofmaxth = dict[date][0] + 300
    widthth = dict[date][1]
    ok = True
#    print 'timeofmaxth = ', timeofmaxth , ' widthth = ', widthth
#    print 'timeofmax = ', timeofmax , ' width = ', width
    if width <widthth -tol*widthth or  width > widthth + tol*widthth:
        ok = False
    if timeofmax <timeofmaxth -tol*timeofmaxth or  timeofmax > timeofmaxth + tol*timeofmaxth:
        ok = False
    return ok

def getexpected(file,date):
    f = open(file,'rb')
    dict = pickle.load(f)
    timeofmaxth = dict[date][0] + 300
    widthth = dict[date][1]
#    print 'timeofmaxth = ', timeofmaxth , ' widthth = ', widthth
    return [timeofmaxth,widthth]


def getthetaphifromfilename(fname):
    filename = fname.split('/')[-1]
    theta = getangle(filename,'theta')
    phi = getangle(filename,'phi')
    return [theta,phi]
#     print filename
#     centertheta = isolatestr(filename,'theta_','_')
#     centerphi = isolatestr(filename,'phi_','_')
#     print centertheta
#     print centerphi
#    theta_-20_-2.5_phi_0_-2.5_expparam_2016_orteguina
    
def getangle(fname,thetaorphi):
    if thetaorphi == 'theta':
        ada = isolatestr(fname,'theta','_phi')
    elif thetaorphi == 'phi':
        ada = isolatestr(fname,'_phi','_exp')
    print ada
    a = isolatestr(ada,'_','_')
    da = ada[ada.rfind('_')+1:]
    angle = float(a) + float(da)
    return angle

def isolatestr(value, a, b):
    # Find and validate before-part.
    pos_a = value.find(a)
    if pos_a == -1: return "vvv"
    # Find and validate after part.
#    pos_b = value.find(b)
    pos_b = value.find(b,pos_a+len(a))
    if pos_b == -1: return "bbb"
    # Return middle part.
    adjusted_pos_a = pos_a + len(a)
    if adjusted_pos_a >= pos_b: return "nnn"
    return value[adjusted_pos_a:pos_b]

def between(value, a, b):
    # Find and validate before-part.
    pos_a = value.find(a)
    if pos_a == -1: return ""
    # Find and validate after part.
    pos_b = value.rfind(b)
    if pos_b == -1: return ""
    # Return middle part.
    adjusted_pos_a = pos_a + len(a)
    if adjusted_pos_a >= pos_b: return ""
    return value[adjusted_pos_a:pos_b]


##################################
#### pattern function   ##########
##################################

def readtwocol(file):
    f = open(file,'r')
    a_doy = np.array([])
    a_flux = np.array([])
    for l in f:
        lsplit = l.split(' ')
        a_doy = np.append(a_doy,int(lsplit[0]))
        a_flux = np.append(a_flux,float(lsplit[1]))
    return [a_doy,a_flux]


def testo():
    print 'testo'
def getpattern(file):
    f = open(file,'r')
    lines = f.readlines()[1:]
    phi = np.array([])
    theta = np.array([])
    gain = np.array([])
    for l in lines:
        lsplit = l.split()
        phi = np.append(phi,float(lsplit[0]))
        theta = np.append(theta,float(lsplit[1]))
        gain = np.append(gain,float(lsplit[2]))
        
    return [phi,theta,gain]

def getpatterntuple(file):
    f = open(file,'r')
    lines = f.readlines()[1:]
    patt = {}
    for l in lines:
        lsplit = l.split()
        phi = int(lsplit[0])
        theta = int(lsplit[1])
        gain = float(lsplit[2])
        angle = (theta,phi)
        patt[angle] = gain    
    return patt

def getpatterntuplefreq(file,frequency):
    f = open(file,'r')
    lines = f.readlines()[5:]
    patt = {}
    for l in lines:
        lsplit = l.split()
        theta = int(lsplit[0])
        for i in range(1,10):
            gain = float(lsplit[i])
            freq = format(3.5 + float(i)/10 - 0.2)
            if format1(freq) == format1(frequency):
                angle = (theta,0)
                patt[angle] = gain
    ######## normalisation ##########
    maxgaindmx = {3.4:8.89767325, 3.5:9.55474198, 3.6:9.67200181, 3.7:8.83030405, 3.8:9.76937185, 3.9:8.7353494,4.0:8.63846581, 4.1:8.37151393, 4.2:8.4945152} 
    maxpower  = np.max(patt.values())
    delta = maxgaindmx[format1(frequency)] - maxpower
    patt2 = {}
    for a,g in zip(patt.keys(), patt.values()):
        newg = g +delta
        patt2[a] = newg
    f.close()
    return patt2

def getpatterntuplefromnpy(file):
    patt = np.load(file+'.npy')
    return patt.item()

#def getpatterntuplefrompkl(file):
def getpatterntuplefrompkl():
    file = '/Users/romain/work/Auger/EASIER/LPSC/suntransit/data/pattern/pattnorsat.pkl'
    with open(file, 'rb') as handle:
        patt = pickle.load(handle)
    return patt

def getclosesttuple(theta,phi,deltheta,delphi):
    newtheta = theta - (theta%deltheta)
    newphi = phi - (phi%delphi)
#    print 'angles :', float("{0:.2f}".format(newtheta)), ' ', float("{0:.2f}".format(newphi))
    return (format(newtheta), format(newphi))
#    return (int(newtheta),int(newphi))

def format(x):
#    print type(x)
    return float("{0:.2f}".format(x))
def format1(x):
#    print type(x)
    return float("{0:.1f}".format(x))

def getclosesttuple2(theta,phi,patt):
    dp = 1000
    dt = 1000
    ph = 0
    th = 0
    da = 1000
    cvec = sphericaltocartesian(np.array([1,degtorad(theta),degtorad(phi)]))
    for p in patt:
        cvec2 = sphericaltocartesian(np.array([1,degtorad(p[0]),degtorad(p[1])]))
        distance = np.linalg.norm(cvec - cvec2)
        if distance < da:
             ph = p[1]
             th = p[0]
             da = distance
    return (th,ph)

from scipy.interpolate import griddata
def interpolatepattern(oldtheta,oldphi,oldgain,newtheta,newphi):
    theta = np.array([])
    phi = np.array([])
    gain = np.array([])
    coord = np.array([oldtheta,oldphi])
    coord = coord.T
    tt, pp = np.meshgrid(newtheta,newphi)
#    newgain = griddata(coord, oldgain, (tt,pp), method='nearest',fill_value=-100)
    newgain = griddata(coord, oldgain, (tt,pp), method='cubic',fill_value=-100)
#    newgain = griddata(coord, oldgain, (tt,pp), method='linear',fill_value=-100)
    newpatt = {}
    for i in range(len(newgain)):
        for t,p,g in zip(tt[i],pp[i],newgain[i]):
            angle = ( float("{0:.2f}".format(t)) , float("{0:.2f}".format(p)) )
            newpatt[angle] = g
    return newpatt
#    print newpatt

def interpolatetraj(theta,phi,size):
    x = np.linspace(0,len(theta),len(theta))
    newx = np.linspace(0,len(theta),10*len(theta))
    newtheta = np.interp(newx,x,theta)
    newphi = np.interp(newx,x,phi)
#    newphi = np.linspace(minp,maxp,size)
    print 'old theta = ', theta, ' new theta = ', newtheta
    print 'old phi = ', phi, ' new phi = ', newphi
    return [newtheta,newphi]
#    print newpatt
    

def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """
    axis = np.asarray(axis)
    theta = np.asarray(theta)
    axis = axis/math.sqrt(np.dot(axis, axis))
    a = math.cos(theta/2.0)
    b, c, d = -axis*math.sin(theta/2.0)
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
    return np.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                     [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                     [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])


def cartesiantospherical(cart):
    norm = np.linalg.norm(cart)
    ncart = cart/norm
    r = 1
    theta = np.arccos(cart[2]/norm)
    phi = np.arctan2(cart[1],cart[0])
    return np.array([norm,theta,phi])

def sphericaltocartesian(spher):
    x = spher[0]*np.sin(spher[1])*np.cos(spher[2])
    y = spher[0]*np.sin(spher[1])*np.sin(spher[2])
    z = spher[0]*np.cos(spher[1])
    return np.array([x,y,z])


def getf107tuple(file):
    f = open(file,'r')
#    lines = f.readlines()[2:]
    lines = f.readlines()
    f107 = {}
    for l in lines:
        lsplit = l.split()
        year = int(lsplit[0])
        doy = int(lsplit[1])
        hour = float(lsplit[2])
        flux = float(lsplit[3])
        date = (year,doy)
        f107[date] = flux
    return f107

def getf107tuplefromcanadian(file):
    f = open(file,'r')
#    lines = f.readlines()[2:]
    lines = f.readlines()
    f107 = {}
    for l in lines[3:]:
        lsplit = l.split()
        year = int(lsplit[0][:4])
        month = int(lsplit[0][4:6])
        day = int(lsplit[0][6:8])
        date = datetime.date(year, month, day)
        doy = datetodoy(date)[1]

        hour = float(lsplit[1])/10000
        flux = float(lsplit[5])
        date = (year,doy)
        f107[date] = flux
    return f107
    
def getfluxtuplefromnobeyama(file):
    f = open(file,'r')
    lines = f.readlines()
    flux = {}
    for l in lines:
        lsplit = l.split()
        year = int(lsplit[0])
        doy = int(lsplit[1])
        theflux = float(lsplit[2])
        date = (year,doy)
        flux[date] = theflux
#        print 'date = ', date, ' flux = ' , flux
    return flux
    

def loaddatafit(path):
    fitfile = open(path,'rb')                                                                                                                                            
    fitdict = pickle.load(fitfile) 
    return fitdict

##############################
# transforms the position given in SPA (sun position algorithm)
# to a set of angle with phi = 0 --> east and phi = 90 --> north
# and zenith = 0
def transformsunpos(thetaspa,phispa):
    theta = np.array([])
    phi = np.array([])
    for t,p in zip(thetaspa,phispa):
        if t == 0 and p == 0:
            theta = np.append(theta,90)
            phi = np.append(phi,90)
        else:
            theta = np.append(theta,90 - t)
            phi = np.append(phi,(-p+90)%360)
    return [theta,phi]

def transformsunposdmx(thetaspa,phispa):
    theta = np.array([])
    phi = np.array([])
    for t,p in zip(thetaspa,phispa):
        if t == 0 and p == 0:
            theta = np.append(theta,90)
            phi = np.append(phi,0)
        else:
            theta = np.append(theta,90 - t)
            phi = np.append(phi,0)
    return [theta,phi]

################################
# transforms the sun position for a vertical antenna to a rotated antenna
# the rotation matrix combines two rotations
def transformtrajectory(theta,phi,rotationmatrix):
    newtheta = np.array([])
    newphi = np.array([])
    for t,p in zip(theta,phi):
        t = degtorad(t)
        p = degtorad(p)
#        if t == 0 and p ==0:
        if t == 90 and p ==90:
            newtheta = np.append(newtheta,90)
            newphi = np.append(newphi,90)
        else:
            cart = sphericaltocartesian([1,t,p])
            rot = np.dot(rotationmatrix,cart)
            rots = cartesiantospherical(rot)
            rots = radtodeg(rots)
            newtheta = np.append(newtheta,rots[1])
            newphi = np.append(newphi,rots[2])
    return [newtheta,newphi]

def getpositiontuple(file):
    f = open(file,'r')
    lines = f.readlines()[1:]
    pos = {}
    doy = 1
    curryear = 0
    for l in lines:
        lsplit = l.split()
        strdate = lsplit[0]
        year = int(strdate[-4:])
        if curryear == 0:
            curryear = year
        elif year != curryear:
            doy = 1
            curryear = year
        theta = lsplit[1::2]
        theta = np.asarray(theta).astype(float)
        phi = lsplit[2::2]
        phi = np.asarray(phi).astype(float)
        date = (year,doy)
#        thetaphi = [90- theta,phi]
        thetaphi = [theta,phi]
        pos[date] = thetaphi
        doy +=1
    return pos
    

#################################
###### time converesion #########
#################################
from datetime import date
import datetime
def gpstodate(gpssecond):
    return  date.fromtimestamp(gpssecond+315964800)
def gpstodatetime(gpssecond):
    return  datetime.datetime.fromtimestamp(gpssecond+315964800)

def tstamptodatetime(tstamp):
#    return  datetime.datetime.fromtimestamp(tstamp + datetime.*3600)
    return  datetime.datetime.utcfromtimestamp(tstamp)
def nptstamptodatetime(tstamp):
    date = np.array([])
    for t in tstamp:
        date = np.append(date,tstamptodatetime(t))
    return  date

def datettotimestamp(dt,utcshift=None):
    if not isinstance(dt, datetime.date):
        print 'you should give a datetime.date or datetime.datetime instance in argument'
        return 
    elif not isinstance(dt, datetime.datetime):
        dt = datetime.datetime(dt.year,dt.month,dt.day) 
    timestamp = (dt - datetime.datetime(1970, 1, 1)).total_seconds()
    if utcshift != None:
        return timestamp + utcshift*3600
    else:
        return timestamp
    
def doytodate(year,doy,hour=None,minute=None):
    if hour == None and minute == None:
        date = datetime.datetime.strptime(str(year)+ ' '+str(doy), '%Y %j')
    elif minute == None:
        date = datetime.datetime.strptime(str(year)+ ' '+str(doy) + ' '+str(hour), '%Y %j %H')
    else:
        date = datetime.datetime.strptime(str(year)+ ' '+str(doy) + ' '+str(hour)+ ' ' +str(minute) , '%Y %j %H %M')
    return date
    
def datetodoy(date):
    year = date.year
    day = int(date.strftime('%j'))
    return (year,day)

def doytoUTC(year,doy,hour=None,minute=None):
    date = doytodate(year,doy,hour,minute)
    tstamp = datettotimestamp(date)
    return tstamp

def secondinday(sec):
    h = int(sec / 3600)
    m = int((sec - h * 3600) / 60)
    s = sec - (h*3600 + m*60)
    if sec == 86400.0:
        return [23,59,59]
    return [int(h),int(m),int(s)]
     
#################################
###### angle conversion  ########
#################################

def degtorad(deg):
    return math.pi*deg/180
def radtodeg(rad):
    return rad*180/math.pi
def zenithtoelev(zenith):
    return 90 - zenith
def elevtozenith(elev):
    return 90 - elev


#################################
###### antenna conversion  ######
#################################

def gaintoaeff(freq,gain):
    c = 3e8 
    lam = c/freq
    aeff = gain*lam**2/(4*math.pi)
    return aeff

def aefftogain(freq,aeff):
    c = 3e8 
    lam = c/freq
    gain = aeff/(lam**2/(4*math.pi))
    return aeff

def dbtolin(v_db):
    return np.power(10,v_db/10)

def lintodb(v_lin):
    return 10*np.log10(v_lin)


def sfutoSI(sfu):
    return sfu*1e-22 # W/m^2/Hz




def gauss(x,a,b,c):
    g = a*np.exp( -((x-b)**2)/(2*c**2) )
    return g

def expofunc(x, a, sigma,mu,b,c):
    return a*np.exp(-((x - mu)/sigma)**2) + b*x + c

def expofuncsimple(x, a, sigma,mu,c):
    return a*np.exp(-((x - mu)/sigma)**2) + c

def hhmmtosecond(hhmm):
    hh = hhmm/100
    mm = hhmm % 100
    sec = hh*3600 + mm*60
    return sec

def sectohhmm(sec):
    h =int(sec/3600)
    m = int(sec%3600)
    hhmm = h*100+m
    return hhmm

def hhmmtohour(hhmm):
    hh = hhmm/100
    mm = hhmm % 100
    sec = hh*3600 + mm*60
    h = hh + mm.astype(float)/60
    return h

## p: point to change (in spherical degree)
## phiangle: the angle the antenna is rotated before tilted [degree]
## invrm: inverse rotation matrix
def changepathref(p,phiangle,invrm,invrm2):
    p = degtorad(p)
    phiangle = degtorad(phiangle)
    # first change the phi angle due to the antenna rotation around z axis 
    #p[2] = p[2] - phiangle
    p = sphericaltocartesian(np.array([1,p[1],p[2] ] ))
    # then change the path because of the rotation in zenith
    p2 = np.dot(invrm2,p)
    print 'p2 = ', radtodeg(cartesiantospherical(p2))
    p2 = np.dot(invrm,p2)
    #    p2 = np.dot(p,invrm)
    p2 = cartesiantospherical(p2)
    #    p2 = -p2
    #    p2[2] = p2[2] + phiangle
    #    p2[2] = p2[2] + phiangle
    p2 = radtodeg(p2)
    return p2

#special function:
# in our case long side of the norsat antenna in on the y axis, 
# so we need to account for 90 deg shift.
def getantaxis(phiangle):
    angle = phiangle - 90
    axis = np.array([np.cos(degtorad(angle)),np.sin(degtorad(angle)),0 ])
    print axis
    return axis


def getdaypos(file):
    z_a = np.array([])    
    a_a = np.array([])
    f = open(file,'r')
    lines = f.readlines()
    for l in lines[4:]:
        lsplit = l.split('\t')
        z_a = np.append(z_a,float(lsplit[1]))
        a_a = np.append(a_a,float(lsplit[2]))
    return [z_a,a_a]

def readoutfile(file):
    f = open(file,'r')
    res = {}
    for l in f:
        ls = l.split()
        y = int(ls[0])
        m = int(ls[1])
        d = int(ls[2])
        date = datetime.datetime(y,m,d)
        res[date] = float(ls[3])
    return res


def getdaysfromlist(filename):
    f = open(filename,'r')
    year = np.array([])
    day = np.array([])
    for l in f:
        lsplit = l.split()
        year = np.append(year,int(lsplit[0]))
        day = np.append(day,int(lsplit[1]))
    return [year,day]



#############################
### fitting function   ######
#############################
from scipy.optimize import curve_fit
def fitwithexpo0(x, y, yerr, a, sigma,mu,c):
    try:
        popt, pcov = curve_fit(expofunc0,x,y,sigma=yerr, p0=[a,sigma,mu,c])
    except RuntimeError:
        print("Error - curve_fit failed")
        return [0.0,0.0]
    return [popt,pcov]

def fitwithexpo0noerr(x, y, a, sigma,mu,c):
    try:
        popt, pcov = curve_fit(expofunc0,x,y, p0=[a,sigma,mu,c])
    except RuntimeError:
        print("Error - curve_fit failed")
        return [0.0,0.0]
    return [popt,pcov]

def fitwithexpo2(x, y, yerr, a, sigma,mu,b,c,d):
    try:
        popt, pcov = curve_fit(expofunc2,x,y,sigma=yerr, p0=[a,sigma,mu,b,c,d])
    except RuntimeError:
        print("Error - curve_fit failed")
        return [0.0,0.0]
    return [popt,pcov]

def gethourarray(datetimearray):
    hourarray = np.array([])
    for d in datetimearray:
        hour = timetohour(d.hour,d.minute)
        hourarray = np.append(hourarray,hour)
    return hourarray

def isgoodfit(fit_max, fit_width, minwidth, maxwidth):
    good = True
    # check time of max:
    if fit_max < 5:
        good = False
#     if fit_tofmax > exp_tofmax + deltatofmax or fit_tofmax < exp_tofmax - deltatofmax:
#         good = False
    if np.abs(fit_width) > maxwidth or np.abs(fit_width) < minwidth:
        good = False
    return good


#################################
### fitting with LMFIT   ########
#################################
from lmfit import minimize, Parameters

def residualgaussexpo2(params, x, data, err_data):
    #a*np.exp(-((x - mu)/sigma)**2) + b*x**2 + c*x + d
    a = params['a']
    mu = params['mu']
    sigma = params['sigma']
    b = params['b']
    c = params['c']
    d = params['d']
    model = expofunc2(x,a,sigma,mu,b,c, d)
    return (data-model)**2/err_data**2

def lmfitgaussexpo2(x, data, err_data, c_tofmax, min_tofmax, max_tofmax, c_sigma, min_sigma, max_sigma):
    params = Parameters()
    params.add('a', value=10)
    params.add('mu', value=c_tofmax)
    params.add('sigma', value=c_sigma)
#    params.add('mu', value=c_tofmax,min=min_tofmax, max=max_tofmax)
#    params.add('sigma', value=c_sigma,min=min_sigma, max=max_sigma)
    params.add('b', value=0)
    params.add('c', value=0)
    params.add('d', value=0)
    out = minimize(residualgaussexpo2, params, args=(x, data, err_data))


def readfitfile(file):
    f = open(file,'r')
    lines = f.read()
    pos1 = lines.find('del(') + 4
    pos2 = lines.find(')\n[[Fit')
    modelname = lines[pos1:pos2]
    
    pos3 = lines.find('# function evals   =')  + len('# function evals   =')
    funceval = int(lines[pos3: pos3+4])

    pos4 = lines.find('# data points      =')  + len('# data points      =')
    datapoints = int(lines[pos4: pos4+4])

    pos5 = lines.find('# variables        =')  + len('# variables        =')
    variables = int(lines[pos5: pos5+4])

    pos6 = lines.find('chi-square         =')  + len('chi-square         =')
    chi2 = float(lines[pos6: pos6 + lines[pos6:].find('\n')])

    pos7 = lines.find('reduced chi-square =')  + len('reduced chi-square =')
    redchi2 = float(lines[pos7: pos7 + lines[pos7:].find('\n')])

    pos8 = lines.find('a: ')  + len('a: ')
    pos9 = pos8 + lines[pos8:].find('+/-')
    a = float(lines[pos8:pos9])
    erra = float(lines[pos9 + len('+/-') : pos9 + lines[pos9:].find('(')])

    pos10 = lines.find('mu: ')  + len('mu: ')
    pos11 = pos10 + lines[pos10:].find('+/-')
    mu = float(lines[pos10:pos11])
    errmu = float(lines[pos11 + len('+/-') : pos11 + lines[pos11:].find('(')])

    pos12 = lines.find('sigma: ')  + len('sigma: ')
    pos13 = pos12 + lines[pos12:].find('+/-')
    sigma = float(lines[pos12:pos13])
    errsigma = float(lines[pos13 + len('+/-') : pos13 + lines[pos13:].find('(')])

    pos14 = lines.find('b: ')  + len('b: ')
    pos15 = pos14 + lines[pos14:].find('+/-')
    b = float(lines[pos14:pos15])
    errb = float(lines[pos15 + len('+/-') : pos15 + lines[pos15:].find('(')])

    pos16 = lines.find('c: ')  + len('c: ')
    pos17 = pos16 + lines[pos16:].find('+/-')
    c = float(lines[pos16:pos17])
    errc = float(lines[pos17 + len('+/-') : pos17 + lines[pos17:].find('(')])

    pos18 = lines.find('d: ')  + len('d: ')
    pos19 = pos18 + lines[pos18:].find('+/-')
    d = float(lines[pos18:pos19])
    errd = float(lines[pos19 + len('+/-') : pos19 + lines[pos19:].find('(')])
#     print funceval
#     print 'datapoints = ',  datapoints
#     print 'variables = ' , variables
#     print 'chi2 = ' , chi2
#     print 'red chi2 = ' , redchi2
#     print 'a = ' , a , ' +- ' , erra
#     print 'mu = ' , mu , ' +- ' , errmu
#     print 'sigma = ' , sigma , ' +- ' , errsigma
#     print 'b = ' , b , ' +- ' , errb
#     print 'c = ' , c , ' +- ' , errc
#     print 'd = ' , d , ' +- ' , errd

    return [modelname,funceval,datapoints,variables,chi2,redchi2,a,erra,mu,errmu,sigma,errsigma,b,errb,c,errc,d,errd]
    
#     # data points      = 72
#     # variables        = 6
#     chi-square         = 2902.238
#     reduced chi-square = 43.973
# [[Variables]]
#     a:       23.1342634 +/- 11.70514 (50.60%) (init= 45.42393)
#     mu:      17.1627538 +/- 0.226672 (1.32%) (init= 18.76667)
#     sigma:   0.65322562 +/- 0.358380 (54.86%) (init= 1)
#     b:      -0.01878266 +/- 0.364420 (1940.20%) (init= 0)
#     c:       1.31551244 +/- 13.35782 (1015.41%) (init= 0)
#     d:      -19.4542934 +/- 118.1887 (607.52%) (init= 0)


