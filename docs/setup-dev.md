# Dev Setup

There are scripts that can help in setting up environment and project for development.
The scripts are in `/dev-setup/<platform>` folder.

**Note**: as of now, we provide scripts for Ubuntu only. It's not guaranteed that the code is working on Windows.

- One needs Python 3.5 to work with the code 
- We recommend using Python virtual environment for development.
- We use pytest for unit and integration testing
- There are some dependencies that must be installed before being able to run the code.

### Quick Setup on Ubuntu 16.04:

This is a Quick Setup for development on a clean Ubuntu 16.04 machine.
Please have a look at the scripts mentioned below to follow them and perform setup manually.

1. Get scripts from `/dev-setup/ubuntu`
1. Run `setup_dev_python.sh` to setup Python3.5, pip and virtualenv
1. Run `setup-dev-depend-ubuntu16.sh` to setup dependencies (charm-crypto, libindy-crypto, libsodium)
1. Fork [indy-plenum](https://github.com/hyperledger/indy-plenum) and [indy-node](https://github.com/hyperledger/indy-node)
1. Go to destination folder for the project.
1. Run `init-dev-project.sh <github-name> <new-virtualenv-name>` to clone indy-plenum and indy-node projects and
create a virtualenv to work in.
1. Activate new virtualenv `workon <new-virtualenv-name>`
1. Now you can run tests by `python setup.py pytest`
1. [Optionally] Install Pycharm
1. [Optionally] Open and configure projects in Pycharm:
    - Open both indy-plenum and indy-node in one window
    - Go to `File -> Settings`
    - Configure Project Interpreter to use just created virtualenv
        - Go to `Project: <name> -> Project Interpreter`
        - You’ll see indy-plenum and indy-node projects on the right side tab.
        For each of them   
            - Click on the project just beside “Project Interpreter” drop down, you’ll see one setting icon, click on it.
            - Select “Add Local”
            - Select existing virtualenv path as below: <virtual env path>/bin/python3.5
          For example: /home/user_name/.virtualenvs/new-virtualenv-name>/bin/python3.5
    - Configure pytest
        - Go to `Configure Tools -> Python Integrated tools`
        - You’ll see indy-plenum and indy-node projects on the right side tab.
        For each of them:
            - Select Py.test from the ‘Default test runner’
    - Press `Apply`
 

### Detailed Setup

##### Setup Python

- One needs Python 3.5 to work with the code.
- Run `setup_dev_python.sh` to setup Python 3.5, pip and virtualenvironment, or have a look at the script, and perform 
necessary steps manually.
