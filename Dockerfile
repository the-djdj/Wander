# Define the docker image
FROM ubuntu:latest
MAINTAINER Dan Jenkins (jenkins.daniel.02@gmail.com)

# Install python3
RUN apt-get update && apt-get install -y python3        \
                                         python3-parted \
                                         python3-yaml

# Copy the sources over into the new machine
COPY . /root

# Ensure that our built machine can be extracted
VOLUME /wander

# And start the wander builder
WORKDIR /root
ENTRYPOINT ["python3"]
CMD ["wander-py/core.py"]
