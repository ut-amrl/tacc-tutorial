#!/bin/bash

# Continuously check the job status for the current user every second
while true; do
    clear
    echo "Checking job status for user $USER..."
    squeue -u "$USER"
    sleep 1
done