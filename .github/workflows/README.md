### Github Actions Workflow

This build file replaces the existing `Jenkins.ci` build process.

`lint.yaml` replaces the `Static code validation` stage of the Jenkins build.

`build.yaml` replaces the `Build / Test` stage of the Jenkins build.

Many of the other stages are replaced merely by the fact we're using Github Actions, we use prebuild Docker containers so we don't have to replicate the steps for building containers.

The `Build result notification` stage was not moved to GHA, build failures will be reports via GHA.

The build process for `Jenkins.nightly` was not ported to GHA.

#### Configuring actions

If you are cloning or forking this repo you will need to configure two secrets for Actions to run correctly.

Secrets can be set via Settings -> Secrets -> New repository secret.

CR_USER is your GH username.
CR_PAT can be created by following [these directions](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token)

Once you have run the build once with those secrets, you have to make then package public.
Access the package at https://ghcr.io/USER/indy-node/indy-node-build or https://ghcr.io/USER/indy-node/indy-node-lint then change the visibility in 'Package Settings' to 'Public' then re-run the build.
