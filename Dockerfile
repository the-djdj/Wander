# Define the docker image
FROM ubuntu:rolling
MAINTAINER Dan Jenkins (https://github.com/the-djdj)

# Allow for a seamless installation
ENV DEBIAN_FRONTEND=noninteractive 

# Install all of the needed packages
RUN apt-get update && apt-get install -y bison              \
                                         build-essential    \
                                         gawk               \
                                         patch              \
                                         python3            \
                                         python3-parted     \
                                         python3-yaml       \
                                         texinfo

# Make sure that the docker is compatible
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# Copy the sources over into the new machine
COPY . /root

# And start the wander builder
WORKDIR /root
ENTRYPOINT ["python3"]
CMD ["wander-py/core.py"]
