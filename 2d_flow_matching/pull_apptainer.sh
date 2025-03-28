#!/bin/bash
module load tacc-apptainer
apptainer pull docker://$DOCKER_USER/2d_flow_matching:latest
