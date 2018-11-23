# Docker base images for Indy projects

This directory contains dockerfiles and necessary resources for images that are supposed to be used as a base layers for different indy docker images. The directory also includes Makefile to automate images building and publishing to Docker Hub.

* [Images Hierarchy](#images-hierarchy)
* [Usage](#usage)

## Images Hierarchy

For now there are three images levels:

 1. [indy-baseimage](#indy-baseimage)
 2. [indy-baseci](#indy-baseci)
 3. [indy-core-baseci](#indy-core-baseci)

Each image is packed with versioning file in the root folder `/*.version` which includes version and commit-sha to make it versioned and matched up with the source code.

### indy-baseimage
Most general purpose image.
Based on **ubuntu:16.04**.
Configures apt for https and installs some common tools (git, wget, vim) and python3.5 with pip, setuptools and virtualenv.

### indy-baseci
Base image for any kind of CI testing images that need [Indy Core apt repository](https://repo.sovrin.org/deb).
Based on [indy-baseimage](#indy-baseimage).
Adds [Indy Core apt repository](https://repo.sovrin.org/deb) to apt sources.list. Also it adds two scripts into system $PATH available directory that could be run by child images to perform common setup routine:

 - `indy_ci_add_user` creates user with python virtualenv configured

### indy-core-baseci
Base image for images that provide CI testing environment for Indy core projects
[indy-plenum](https://github.com/hyperledger/indy-plenum),
[indy-node](https://github.com/hyperledger/indy-node)).
Based on  [indy-baseci](#indy-baseci).
Adds [Indy SDK apt repository](https://repo.sovrin.org/sdk/deb) to apt sources.list and configures apt preferences to make indy sdk packages from Indy Core apt repo more prioritized than from Indy SDK repo.

## Usage


### Build

`make`

Builds all three base images tagged according to version from `*.version` files.


### Publish

Before making push to Docker Hub the one should keep in mind:

 - each base image includes versioning file with the information about commit-sha inside
 - any changes should pass CI verification before release

Thus, the following release workflow is expected:

 1. update dockerfile(s) and/or related resources
 2. bump versions in `*.version` and base images tags in `*.dockerfile` accordingly. **Note**: each update in one of base images leads to version update for the child images as well
 3. create PR to [master](https://github.com/hyperledger/indy-node/tree/master/)
 4. pull [master](https://github.com/hyperledger/indy-node/tree/master/) locally once it is merged
 5. do `make publish`
