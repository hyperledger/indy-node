# GitHub Actions Workflows

The  [PR](PR.yaml) workflow runs on Pull Requests to the main branch,
which only contain changes to python files. If no python file is affected it doesn't run.
The same applies to the [Push](Push.yaml) workflow respectively for pushes.

The [tag](tag.yaml), [releasepr](releasepr.yaml) and [publishRelease](publishRelease.yaml) workflows are used for the new [Release Workflow](../../docs/release-workflow.png).
They use reuseable workflows from the [indy-shared-gha](https://github.com/hyperledger/indy-shared-gha) repository and the following workflow in this folder.

+ [reuseable_test.yaml](reuseable_test.yaml)
   This workflow runs the tests inside the uploaded docker images.