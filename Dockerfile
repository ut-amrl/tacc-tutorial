ARG PYTORCH="2.1.2"
ARG CUDA="12.1"
ARG CUDNN="8"

# Add CUDA support
FROM pytorch/pytorch:${PYTORCH}-cuda${CUDA}-cudnn${CUDNN}-devel AS pytorch

ENV TORCH_CUDA_ARCH_LIST="6.0 6.1 7.0 7.5 8.0 8.6+PTX" \
    TORCH_NVCC_FLAGS="-Xfatbin -compress-all" \
    CMAKE_PREFIX_PATH="$(dirname $(which conda))/../" \
    FORCE_CUDA="1"

ENV TZ=US \
    DEBIAN_FRONTEND=noninteractive

# Minimal setup
RUN apt-get update \
 && apt-get install -y locales lsb-release
ARG DEBIAN_FRONTEND=noninteractive
RUN dpkg-reconfigure locales

# Install the required packages
RUN apt-get update && apt-get -y upgrade 
RUN apt-get install -y ffmpeg libsm6 libxext6 git vim ninja-build libglib2.0-0 libsm6 libxrender-dev libxext6 lsb-core \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install ROS Noetic
RUN sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
RUN apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
RUN apt-get update \
 && apt-get install -y --no-install-recommends ros-noetic-desktop-full
RUN apt-get install -y --no-install-recommends python3-rosdep
RUN rosdep init \
 && rosdep fix-permissions \
 && rosdep update
RUN echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc

COPY . /tacc-tutorial
WORKDIR /tacc-tutorial