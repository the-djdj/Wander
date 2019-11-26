# Define the docker image
FROM ubuntu:latest
MAINTAINER Dan Jenkins (jenkins.daniel.02@gmail.com)

# Install python3
RUN apt-get update && apt-get install -y python3        \
                                         python3-parted \
                                         python3-yaml

# Make sure that the docker is compatible
RUN rm /bin/sh && ln -s /bin/bash /bin/sh
RUN apt-get install -y bison
RUN apt-get install -y gawk
RUN apt-get install -y gcc
RUN apt-get install -y g++
RUN apt-get install -y make
RUN apt-get install -y patch
RUN apt-get install -y texinfo

# Copy the sources over into the new machine
COPY . /root

# And start the wander builder
WORKDIR /root
ENTRYPOINT ["python3"]
CMD ["wander-py/core.py"]
