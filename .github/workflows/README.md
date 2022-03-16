# GitHub Actions Workflow

The workflow in the [push_pr.yaml](push_pr.yaml) file runs on push and pull requests to the ubuntu-20-04-upgrade branch.
It uses the following reusable workflows in this folder.

+ [buildimage.yaml](buildimage.yaml)
   This workflow builds the dockerimages and pushes them to the GHCR.
+ [test.yaml](test.yaml)
   This workflow runs the tests inside the uploaded docker images.
+ [buildpackages.yaml](buildpackages.yaml)
   This workflows builds the python and debian packages. It also uploads them to the workflow.
+ [publish_artifacts.yaml](publish_artifacts.yaml)
   This workflow uploads the packages to PYPI and Artifactory.