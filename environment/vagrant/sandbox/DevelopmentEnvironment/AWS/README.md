This is a Vagrant project. Please read the "README" at the top of the Vagrantfile
before running `vagrant up`.

## TODO
3. All "Dependencies" are built from source. See "Dependencies" section in
   config.properties. Modify the dependencies list (comma separated list) to
   accept a comma sepparated list of <dep>=<version> strings. When "=<version>"
   is present, install the specific version of the package via the package
   manager instead of building it from source.

## Objectives

1. Instantiate an Indy AWS Development Environment with all of the tools and
   source code needed to contribute to any Indy AWS project.
2. All CI/CD targets (clean, build, test, bundle, deposit, and deploy) should be
   identical or nearly identical to their counterparts in the Jenkins CI/CD
   pipelines (if applicable). Please read scriptlets/README.md for more details.
3. It must be easy to add new projects/repos.
   Note: config.properties and scriptlets (directory) provide a modular
         interface.
4. Allow a developer to configure each repository's expected post-provisioning
   state. A config.properties file must allow a developer to dictate what happens
   to each repository during provisioning.
5. Provide a way for developers to reuse CI/CD scriptlets during the development
   lifecycle. `vagrant ssh` to the development VM and then run `helprepo`.

## Typical Use

1. Run `vagrant up`
2. Run `vagrant ssh`
3. Once on the Vagrant guest (aws.lambda.development), run `userepo <repo>` where
   <repo> is the name one of the repos you have configured in config.properties.
   Note that the name of the repo is prepended to the PS1 prompt.
   Example: After running `userepo indy-self-serv`, the PS1 prompt will display
            `(indy-self-serv)vagrant@aws.labmda.development:~$`
4. Run `helprepo` to see available CI/CD commands and usage information or take
   a look at the /home/ec2-user/.bashrc for aliases and exported functions.

### Example

```bash
$ vagrant up
$ vagrant ssh
vagrant@development:~$ userepo agency
Switching CI/CD context to repo agency
(agency)vagrant@aws.lambda.development:~$ helprepo
Usage: userepo <repo> - set repo context
Usage: helprepo - print usage and help information
Usage: *repo - CI/CD targets - see Aavailable commands below

Available commands:
-------------------
buildrepo
bundlerepo
cdrepo
cleanrepo
deployrepo
depositrepo
helprepo
setuprepo
testrepo
unsetrepo
userepo
whichrepo

Settings:
---------
package_manager=apt
scriptlets_directory=/vagrant/scriptlets
current_repo=agency
repo_scriptlet_path=/vagrant/scriptlets/agency
```
