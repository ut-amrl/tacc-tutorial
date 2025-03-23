#!/bin/bash
# run_docker.sh
# Usage: ./run_docker.sh <path_to_train_py_directory> [additional args for train.py]

# Check that the train.py directory is provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <path_to_tacc_tutorial_directory> [additional args for train.py]"
    exit 1
fi

# Get the absolute path to the directory containing train.py
TRAIN_DIR=$(realpath "$1")
shift

# Docker image name
IMAGE_NAME="tacc-tutorial-flow"
CONTAINER_TRAIN_DIR="/home/tacc-tutorial"

echo "Building Docker image: $IMAGE_NAME"
docker build -t "$IMAGE_NAME" .

echo "Running Docker container..."

# Run the container with the provided directory mounted as /home
docker run --rm --gpus all -v "$TRAIN_DIR":$CONTAINER_TRAIN_DIR "$IMAGE_NAME" python3 -u $CONTAINER_TRAIN_DIR/2d_flow_matching/train.py "$@"

# python3 -u /home/train.py "$@"