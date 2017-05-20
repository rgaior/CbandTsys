import sys
import os
for st in ['domo','vieira','chape','popey']:
    script = "python producedailysim.py " + st + " -list newlist_"+ st + ".txt"
    print script
    os.system(script)
