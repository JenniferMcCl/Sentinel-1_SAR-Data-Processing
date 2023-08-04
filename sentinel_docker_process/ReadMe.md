# Sentinel-1 SAR processing with Docker on remote machine

## How to install Docker on Ubuntu Focal 20.04
- Follow general steps on 
https://docs.docker.com/engine/install/ubuntu/ 

```Make sure to uninstall Ubuntu Docker Version first!!!```

### Post installation steps for convenience:
- Included in: https://docs.docker.com/engine/install/linux-postinstall/

1. Create a docker group via "sudo groupadd docker"
2. Add your user to group via "sudo usermod -aG docker $USER"
3. Execute "newgrp docker" to update changes

### Location of ESA Snap 9.0 Docker Image (included in Docker file)
https://hub.docker.com/r/mundialis/esa-snap 

## Run Docker with Docker Compose:
- General information: https://docs.docker.com/compose/gettingstarted/

- How to manually start docker daemon:
https://docs.docker.com/config/daemon/start/

- Test Docker via:
1. "docker start hello-world"
2. "docker run hello-world"

## Build a Docker Container with Docker Image File for processing Sentinel-1-SAR Data:

- After successful installation of Docker download the "sentinel_docker_process" folder into your desired user space.

- Clone the repository https://gitea.julius-kuehn.de/FLF/Sentinel-1-SLC-process into the "processing-tool" folder.
Alternatively for accessible alternative Git servers (Bitbucket, Git-Hub) uncomment git related area in Docker file and replace key name and repository server name.

- Replace "AOI.geojson" file in "processing_tool" folder with geojson file containing desired AOI for processing.
- In user_settings.xml file set all settings accept for: data, cohOutput, backscatterOutput, vegIdOutput. These paths are set to redirect processed data outside of container.

- Navigate to "sentinel_docker_process" folder containing Dockerfile
Execute "docker build -t jki/sentinel-1-processing:1 ." to build Docker image

- Execution of Container with bind mounts: https://docs.docker.com/storage/bind-mounts/

```Make sure to replace <output folder path> with the desired path to contain the processed data.```

"docker run -it --mount type=bind,source=/codede,target=/codede --mount type=bind,source=<output folder path>,target=/development/test_output jki/sentinel-1-processing:1


- In the shell of the running container execute standard steps to execute processing chain via Readme of Sentinel-1-SLC-process repository. https://gitea.julius-kuehn.de/FLF/Sentinel-1-SLC-process/src/branch/master/README.md

### Convenience Docker Commands

- list contents “docker ps”
- list images “docker images ls”
- free cache when blocked by Docker content „docker system prune“ 



