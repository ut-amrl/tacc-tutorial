#!/bin/bash
#----------------------------------------------------
# Sample Slurm job script
#   for TACC Lonestar6 AMD Milan nodes
#
#   *** Serial Job in Normal Queue***
# 
# Last revised: March 23, 2025
#
# Notes:
#
#  -- Copy/edit this script as desired.  Launch by executing
#     "sbatch slurn_sweep.sh"
#
#  -- Executes a parametric sweep over the number of hyperparameters.
#
#  -- Use TACC's launcher utility to run multiple serial 
#       executables at the same time, execute "module load launcher" 
#       followed by "module help launcher".
#----------------------------------------------------

#!/bin/bash
#SBATCH -p gpu-a100                 # queue (partition) 
#SBATCH -J flow-matching-sweep      # job name
#SBATCH -o pylauncher.o%j           # output file name (%j expands to SLURM jobID)
#SBATCH -e pylaunchertest.o%j       # error file name (%j expands to SLURM jobID)
#SBATCH -n 3          # needs to match #gpus on each node
#SBATCH -N 1                        # number of nodes requested
#SBATCH -t 00:15:00                 # run time (hh:mm:ss) 
#SBATCH -A MLL                      # Allocation name to charge job against

module load pylauncher
module load python3
module load cuda/12.2
module load tacc-apptainer

python3 launcher.py