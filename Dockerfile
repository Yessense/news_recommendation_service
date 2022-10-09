FROM nvcr.io/nvidia/cuda:11.1.1-devel-ubuntu20.04

ENV DEBIAN_FRONTEND noninteractive


# Install system dependencies for convinient development inside container
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    tmux \
    openssh-server \
    tree \
    less \
    vim \
    curl \
    wget \
    build-essential \
    python3-pip \
    mesa-utils \
    sudo \
    && rm -rf /var/lib/apt/lists/*



RUN pip3 install torch==1.9.0+cu111 -f https://download.pytorch.org/whl/torch_stable.html
RUN pip3 install transformers==4.22.2 flask==2.2.2

EXPOSE 22
EXPOSE 8080

# add user and his password
ARG USER=docker_user
ARG UID=1000
ARG GID=1000

# default password
ARG PW=user


RUN useradd -m ${USER} --uid=${UID} && echo "${USER}:${PW}" | chpasswd && adduser ${USER} sudo
WORKDIR /home/${USER}
RUN mkdir -p /src && chown -R ${UID}:${GID} /home/${USER}
ADD src/models src/models/
ADD src/embedder.py src/embedder.py
USER ${UID}:${GID}