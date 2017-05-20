#################################
##### definition of folders #####
#################################
#folder with root file produced by Corinne's code
datafolder = '/Users/romain/work/Auger/EASIER/LPSC/monitoring/data/'
GDrootfilefolder = datafolder + 'GIGADuck/'
#uncertainty on the pattern (not necessary anymore)
aeffuncertfolder = '/Users/romain/work/Auger/EASIER/LPSC/suntransit/data/uncertainty/'

#main folder:
mainfolder = '/Users/romain/work/Auger/EASIER/LPNHE/finalGD_Tsys/'
#name of folder says it all:
scriptfolder = mainfolder + '/script/'
datafolder = mainfolder + '/data/'
#simresultfolder = '/Users/romain/work/Auger/EASIER/LPNHE/newnewGD_Tsys/sim/'
simresultfolder = mainfolder + '/sim/'
tempfitfolder = mainfolder + '/tempfit/'
resfolder = mainfolder+ '/results/'
datafitfolder = mainfolder+ '/datafit/'
datafit2folder = mainfolder+ '/datafit2/'
listfolder = mainfolder + '/list/'
plotfolder = mainfolder + '/plots/'
contourfolder = mainfolder + '/contour/'


#################################
##### geometric and timing ######
#################################
exptime =  {384:16.00,385:17.30, 427:15.00, 431:18., 433:16.00 , 330:16.00, 328:16.00,329:17.30,313:17.30, 334:15.00, 340:18.,339:16.00}
GDantennageo = {'luis':(-20,60),'juan':(-20,120),'domo':(20,0),'chape':(20,60),'popey':(20,120),'orteguina':(-20,0),'vieira':(0,0)}
Helixantennageo = {'rula':(-20,60),'gringa':(-20,120),'gilda':(20,0),'eva':(20,60),'jorge':(20,120),'nono':(-20,0),'santy':(0,0)} 
GDnametom = {'popey':1500,'vieira':1400,'domo':1200,'orteguina':1600,'chape':1200}                                                      
Helixnametom = {'jorge':1500,'santy':1400,'gilda':1200,'nono':1600,'eva':1200}                    
doy = {2011:365,2012:366,2013:365,2014:365,2015:365,2016:366,2017:60}

#################################
##### station names and id ######
#################################
EA7stationidbyname = {'concorde':333,'bastille':332,'leandro':341,'nene':342,'paloma':343,'magali':344,'josemaria':419}                      
EA7stationnamebyid = dict(zip(EA7stationidbyname.values(),EA7stationidbyname.keys()))                                                         

GDstationidbyname = {'vieira':433,'luis':422,'orteguina':431,'popey':385,'chape':384,'domo':427,'juan':432}                        
GDstationnamebyid =  dict(zip(GDstationidbyname.values(),GDstationidbyname.keys()))                                                  

Helixstationidbyname = {'santy':339,'rula':313,'nono':340,'jorge':329,'eva':330,'gilda':334,'gringa':328}                               
Helixstationnamebyid =  dict(zip(Helixstationidbyname.values(),Helixstationidbyname.keys()))      
GIGASstationidbyname = {'santy':339,'rula':313,'nono':340,'jorge':329,'eva':330,'gilda':334,'gringa':328,'vieira':433,'luis':422,'orteguina':431,'popey':385,'chape':384,'domo':427,'juan':432}
GIGASstationidbyid = dict(zip(GIGASstationidbyname.values(),GIGASstationidbyname.keys()))      
ARTtoUTC = 3



###################################
##### sun transit simulation ######
###################################
basefolder = '/Users/romain/work/Auger/EASIER/LPSC/suntransit/'
patternfolder = basefolder +'data/pattern/'
uncertfolder =  basefolder + '/data/uncertainty'
gainfiledmx = patternfolder + 'Mon_GI301SC-ColRad1.txt'
gainfiledmx2 = patternfolder + 'WSI_ring_radome_E.txt'
gainfilenorsat = patternfolder + 'HFSSDesign5_AINFO_15db_rad.txt'
gainfilenorsat2 = patternfolder + 'HFSSDesign5_AINFO_15db_rad_interp0_1'
gainfilehelix = patternfolder + 'HELIX_FPV_5_50ohm_Cone.txt'
f107fileCanada = basefolder + 'data/canadian.txt'
f107fileUS = basefolder + 'data/sunfluxall.dat'
nobeyamafile = basefolder + 'data/nobeall.txt'
nobeyamafileL = basefolder + 'data/nobeallL.txt'
 

#############################
##### detector numbers ######
#############################
adctop = 48.7


####################################
##### data selection constnat ######
####################################
diffmax = 200
diffmin = 10
rmsmin = 2
finallimrms = 10





##################################
# constant factor to get the chi2 to one:
tsysfactor = {'vieira':1.45,'luis':1,'orteguina':4,'popey':2.64,'chape':1.11,'domo':2.65,'juan':1}
tofmaxfactor = {'vieira':2.79,'luis':1,'orteguina':4.6,'popey':3.65,'chape':1.10,'domo':3.93,'juan':1}
nroffitmax = {'vieira':2.79,'luis':1,'orteguina':3.8,'popey':3.65,'chape':1.10,'domo':105,'juan':1}






