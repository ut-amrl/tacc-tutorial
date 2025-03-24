## file: launcher.py 
import pylauncher 
pylauncher.GPULauncher\
    ("gpucommandlines",             # Uses GPU specific launcher
     debug="host+job",              # Basic debug output, verbose setting: host+exec+task+job+ssh
    #  workdir="pylauncher_out",    # Uncomment to set output directory, must be unique per run
     gpuspernode=3                  # adjust for the desired cluster
     )