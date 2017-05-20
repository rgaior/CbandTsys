import sys
import os
theta = range(0,30,1)
phi = range(-30,30,1)
for t in theta:
    for p in phi:
        script = "python analysecheck.py orteguina 2"
        torun = script + " --deltatheta " + str(t) + " --deltaphi " + str(p)
        print torun
        os.system(torun)
