import sys
import os
theta = range(-30,31,1)
phi = range(-30,31,1)
for t in theta:
    for p in phi:
        script = "python producedailysim.py orteguina -list update_orteguina.txt"
        torun = script + " --theta " + str(t) + " --phi " + str(p)
        print torun
        os.system(torun)
