#Run: "docker build -t jki/sentinel-1-processing:1 ."

FROM mundialis/esa-snap:ubuntu

# Install base utilities
RUN apt-get update && apt-get install -y wget && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install miniconda
ENV CONDA_DIR /opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && /bin/bash ~/miniconda.sh -b -p /opt/conda
#Installation for whole version: Anaconda3-2021.11-Linux-x86_64.sh

# Put conda in path so we can use conda activate
ENV PATH=$CONDA_DIR/bin:$PATH

RUN conda install python=3.9
RUN conda install -c conda-forge pyrosar
RUN conda install -c conda-forge sentinelsat
RUN conda install -c conda-forge geojson
RUN conda install -c conda-forge geomet
RUN conda install -c conda-forge geopandas-base
RUN conda install -c conda-forge gettext
RUN conda install -c conda-forge gitpython
RUN conda install -c conda-forge pandas
RUN conda install -c conda-forge requests
RUN conda install -c conda-forge numpy
RUN conda install -c conda-forge rasterio
RUN conda install -c conda-forge openssh
RUN conda install -c conda-forge pyogrio

#RUN python --version 

##---------This is optional for accesing git directly------------------##
##---------Is not workgin for JKI Gitea--------------------------------##

## Install git software 
RUN apt-get install -y git

## Make ssh dir
#RUN mkdir /root/.ssh/

## Copy over private key, and set permissions
## Warning! Anyone who gets their hands on this image will be able
## to retrieve this private key file from the corresponding image layer
#ADD id_ed25519 /root/.ssh/id_ed25519
#ADD known_hosts /root/.ssh/known_hosts

## Add gitea key
#RUN ssh-keyscan gitea.julius-kuehn.de >> /root/.ssh/known_hosts

## Clone the conf files into the docker container
##Access denied by Gitea, should work on other servers
#RUN ssh-keyscan gitea.julius-kuehn.de >> /root/.ssh/known_hosts
#RUN git clone https://gitea.julius-kuehn.de/FLF/Sentinel-1-SLC-process.git

RUN mkdir /codede
RUN mkdir /processing_tool
COPY /processing_tool /processing_tool


