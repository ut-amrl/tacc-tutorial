#!/bin/bash
#----------------------------------------------------
# Sample Slurm job script
#   for TACC Lonestar6 AMD Milan nodes
#
#   *** Serial Job in Normal Queue***
# 
# Last revised: October 22, 2021
#
# Notes:
#
#  -- Copy/edit this script as desired.  Launch by executing
#     "sbatch test_launcher.sh"
#
#  -- Executes a parametric sweep over the number of MPI tasks (32 in this case).
#
#  -- Use TACC's launcher utility to run multiple serial 
#       executables at the same time, execute "module load launcher" 
#       followed by "module help launcher".
#----------------------------------------------------

#!/bin/bash
#SBATCH -J mpi-test                 # job name
#SBATCH -o launcher.o%j             # output and error file name (%j expands to SLURM jobID)
#SBATCH -N 2                        # number of nodes requested
#SBATCH -n 32                       # total number of tasks to run in parallel
#SBATCH -p gpu-a100                 # queue (partition) 
#SBATCH -t 00:15:00                 # run time (hh:mm:ss) 
#SBATCH -A YOUR_ALLOCATION          # Allocation name to charge job against

module load python3
module load cuda/12.0
module load tacc-apptainer

# Launcher not compatible with MPI containers, launch with task_affinity

# 128 tasks; offset by  0 entries in hostfile.
ibrun -n 16 -o  0 task_affinity singularity exec --nv tacc-tutorial.sif python test_mpi.py --job_id 0 > output/job0.txt &   

# 128 tasks; offset by 16 entries in hostfile.
ibrun -n 16 -o 16 task_affinity singularity exec --nv tacc-tutorial.sif python test_mpi.py --job_id 1 >  output/job1.txt & 

# Required; else script will exit immediately.
wait
