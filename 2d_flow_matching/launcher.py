## file: launcher.py
import pylauncher 
pylauncher.GPULauncher\
    ("gpucommandlines",
     debug="job",
     gpuspernode=3 # adjust for the desired cluster
     )