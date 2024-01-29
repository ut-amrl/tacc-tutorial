# tacc-tutorial

This repository contains the materials for the TACC tutorial on deploying MPI GPU applications on Lonestar6. This tutorial assumes that you have already installed and configured Docker on your local machine. If you have not done so, please follow the instructions [here](https://docs.docker.com/get-docker/).

## Getting Started

### Logging in to Lonestar6

To log in to Lonestar6, you will need to have an account on the TACC system. If you do not have an account, 
you can request one [here](https://portal.tacc.utexas.edu/account-request).

Once you have an account, you can log in to Lonestar6 using the following command:

```bash
ssh <username>@ls6.tacc.utexas.edu
```

### Registering on Docker Hub

To register on Docker Hub, go to [https://hub.docker.com/signup](https://hub.docker.com/signup) and follow 
the instructions. Once you have registered, you will need to log in to Docker Hub locally. To do so, run 
the following command:

```bash
docker login
```

### Cloning the Repository

Once you have logged in to Lonestar6, you will need to clone this repository. To do so, run the following command:

```bash
git clone git@github.com:ut-amrl/tacc-tutorial.git
cd tacc-tutorial
```

### Building the Docker image locally

To build the Docker image locally, and run the following command from the root of the repository. Replace `<username>` with your Docker Hub username.

```bash
docker build -t <username>/tacc-tutorial Dockerfile .
```

### Running the Docker image locally

To run the Docker image locally, run the following command from the root of the repository. Replace `<username>` with your Docker Hub username.

```bash
docker run -it --rm <username>/tacc-tutorial python test_mpi.py --job_id 0
```

If it works, you should see the following output. Note that the CUDA device name may be different.

```
Started job on TACC with id 0
CUDA available: True
CUDA device count: 3
CUDA device name: NVIDIA A100-PCIE-40GB
CUDA current device: 0
mat1: tensor([[-0.6334,  1.0846, -1.0990],
        [-0.0802,  0.1045, -1.1741],
        [-1.2013,  0.5301, -0.3516]], device='cuda:0')
mat2: tensor([[ 2.9519,  1.9436,  1.5096,  0.8988],
        [-0.4903, -0.2861, -0.8897, -0.5607],
        [-1.3142,  0.8620, -0.4177,  0.0652]], device='cuda:0')
mat1 @ mat2 tensor([[-0.9572, -2.4887, -1.4620, -1.2492],
        [ 1.2551, -1.1977,  0.2765, -0.2073],
        [-3.3439, -2.7895, -2.1382, -1.3999]], device='cuda:0')
Finished job on TACC with id 0
```

## Deploying the Docker image on Lonestar6

### Pushing the Docker image to Docker Hub

To push the Docker image to Docker Hub, run the following command from the root of the repository. Replace `<username>` with your Docker Hub username.

```bash
docker push <username>/tacc-tutorial
```

### Setting up Singularity on Lonestar6

Next, you will need to build the image on Lonestar6. To do so, log in to Lonestar6 and run the following commands. 

```bash
cd $SCRATCH
git clone git@github.com:ut-amrl/tacc-tutorial.git
idev -m 30 -p gpu-a100-small
module load tacc-apptainer
singularity build tacc-tutorial.sif docker://<username>/tacc-tutorial
```

Alternatively, you may wish to simply pull the image from Docker Hub. instead To do so, replace the final command with the following:

```bash
singularity pull tacc-tutorial.sif docker://<username>/tacc-tutorial
```

### Running the Singularity image on Lonestar6

We will need to create a job script to run the Singularity image on Lonestar6. To do so, we will use the `launch_mpi.bash` file, which launches two singularity containers on two nodes. For each node, it will spawn 16 processes and print a simple matrix multiplication to a file in the `output` directory as `job<JOBID>.txt`. You will need to modify the following line in the `launch_mpi.bash` file to use your allocation name

```coda
#SBATCH -A YOUR_ALLOCATION          # Allocation name to charge job against
``````

We will use the `sbatch` command to submit the job to the job scheduler. To do so, run the following command:

```bash
sbatch launch_mpi.bash
```

## Monitoring Submitted Jobs

To check the status of the job, run the following command:

```bash
squeue -u <username>
```

You should see something like the following:

```
arthurz@login1$ squeue -u arthurz
JOBID   PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
1486058    gpu-a100 mpi-test  arthurz  R       0:01      2 c303-[002-003]
```

Once the job has started, we can monitor the progress of the job by looking at the output files. To do so, run the following commands to monitor jobs 0 and 1 respectively:

```bash
tail -fn +1 output/job0.txt
tail -fn +1 output/job1.txt
```

If we inspect job0.txt, we should see the same output repeated 16 times for each process that we spawned on the first node.

```bash
cat output/job0.txt | grep Finished
```

Expected Output:
```text
Finished job on TACC with id 0
Finished job on TACC with id 0
Finished job on TACC with id 0
Finished job on TACC with id 0
Finished job on TACC with id 0
Finished job on TACC with id 0
Finished job on TACC with id 0
Finished job on TACC with id 0
Finished job on TACC with id 0
Finished job on TACC with id 0
Finished job on TACC with id 0
Finished job on TACC with id 0
Finished job on TACC with id 0
Finished job on TACC with id 0
Finished job on TACC with id 0
Finished job on TACC with id 0
```

Congratulations! You have successfully deployed a multi-process, multi-GPU job on Lonestar6!