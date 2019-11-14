# Wander
A simple Wander Linux builder implemented in Python.

## What is it?
Wander Linux is a linux distribution based on the [Linux From Scratch](linuxfromscratch.org) project. It provides a simple, fast, linux distribution tailored specifically to your device's hardware by compiling each package from scratch. All of the configuration files are easily changable and human-readable, providing great opportunities for customisation!

## How does it work?
The Wander Linux builder downloads source packages and uses those to construct a temporary system upon which Wander will be built. Once this is done, packages are added to the system as they are needed.

All information about what packages are needed where and what they need to do are stored in a series of `YAML` files. This means that anybody can change their Wander to meet their exact requirements without having to delve heavily into code.

## What do I need?

### Dependencies
The Wander Linux builder is written entirely in Python 3 and tested using Python 3.7, although other Python 3 version will probably work. 

Two special python packages are required;
* `pyparted`, a Python wrapper for `fdisk`, and
* `pyyaml`, a Python `YAML` interpreter.

Both of these dependencies can be installed using `pip3 install pyparted pyyaml`.

The other dependencies are inherent to the operating system build process, and can thus vary from build to build. These dependencies can be found in `prerequisites.yaml`, and are tested whenever the Wander Linux builder starts up.

### Distribution
This system has been tested on Ubuntu 19.10 and Slackware 14.2, on 64- and 32-bit hardware, respectively. If you are using another distribution, you may need an additional amount of tweaking, but it should nevertheless be possible to run this smoothly.

### Storage
Wander requires a dedicated partition on which its filesystem will be built. Once it has completed, you can archive this system and use it elsewhere, but a partition with at least **12 GB** of free space is required for the build process. The final system will be much smaller than this, but this allows for debug headers and sources to be stored, before they are later stripped.

## How do I run it?
To run the Wander Linux build system, issue the following as root:
```shell
python3 wander-py/core.py
```
You will then be able to choose a Wander version to build, whereafter the system will check that you meet the prerequisites for the build, and find your partition. This process will take quite a while, and it is advised that you allow it to run through the entire build without stopping. If you do need to stop however, you can skip packages which have already been built by adding `skip: true` underneath the package name in the respective `YAML` file.

**Please** make a backup of your system before you run this - a badly configured Wander build script can destroy your machine. Additionally, always ensure that you are either building a release of Wander, or are on the `stable` branch of this repository.

## How do I get involved?

Whether you want to develop the core builder itself, work on new Wander distributions, or just maintain packages in the older ones, feel free to fork this repo and submit your pull requests. Similarly, anybody is free to create issues and we'll try to resolve them as soon as possible. 
