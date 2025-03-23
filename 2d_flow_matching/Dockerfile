ARG PYTORCH="2.4.0"
ARG CUDA="12.1"
ARG CUDNN="9"

# Use the prebuilt PyTorch container with CUDA support
FROM pytorch/pytorch:${PYTORCH}-cuda${CUDA}-cudnn${CUDNN}-devel AS pytorch

# Install necessary system dependencies (git is needed to clone the flow_matching repository)
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Install only the necessary Python packages (torch is pre-installed)
RUN pip3 install matplotlib numpy flow_matching

# Clone and install the flow_matching repository in editable mode.
# Replace the URL with the correct repository if needed.
# RUN git clone https://github.com/yourusername/flow_matching.git && \
#     pip3 install -e flow_matching

# The container expects that train.py and other files will be mounted as a volume.
CMD ["python3", "/home/tacc-tutorial/2d_flow_matching/train.py", "--help"]
