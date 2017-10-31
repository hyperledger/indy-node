# Dev Setup

There are scripts that can help in setting up environment and project for developers.
The scripts are in [dev-setup](https://github.com/hyperledger/indy-node/tree/master/dev-setup) folder.

**Note**: as of now, we provide scripts for Ubuntu only. It's not guaranteed that the code is working on Windows.

- One needs Python 3.5 to work with the code 
- We recommend using Python virtual environment for development.
- We use pytest for unit and integration testing
- There are some dependencies that must be installed before being able to run the code.

## Quick Setup on Ubuntu 16.04:

This is a Quick Setup for development on a clean Ubuntu 16.04 machine.
You can also have a look at the scripts mentioned below to follow them and perform setup manually.

1. Get scripts from [dev-setup-ubuntu](https://github.com/hyperledger/indy-node/tree/master/dev-setup/ubuntu)
1. Run `setup_dev_python.sh` to setup Python3.5, pip and virtualenv
1. Run `setup-dev-depend-ubuntu16.sh` to setup dependencies (charm-crypto, libindy-crypto, libsodium)
1. Fork [indy-plenum](https://github.com/hyperledger/indy-plenum) and [indy-node](https://github.com/hyperledger/indy-node)
1. Go to the destination folder for the project.
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
    - Configure Project Dependency
        - Go to `Project: <name> -> Project Dependencies`
        - Mark each project to be dependent on another one
    - Configure pytest
        - Go to `Configure Tools -> Python Integrated tools`
        - You’ll see indy-plenum and indy-node projects on the right side tab.
        For each of them:
            - Select Py.test from the ‘Default test runner’
    - Press `Apply`
 

## Detailed Setup

### Setup Python

One needs Python 3.5 to work with the code.

You can use `dev-setup/ubuntu/setup_dev_python.sh` script for Quick installation of Python 3.5, pip 
and virtualenvironment on Ubuntu, or follow the detailed instructions below.


##### Ubuntu

1. Run ```sudo add-apt-repository ppa:fkrull/deadsnakes```

2. Run ```sudo apt-get update```

3. On Ubuntu 14, run ```sudo apt-get install python3.5``` (python3.5 is pre-installed on most Ubuntu 16 systems; if not, do it there as well.)

##### CentOS/Redhat

Run ```sudo yum install python3.5```

##### Mac

1. Go to [python.org](https://www.python.org) and from the "Downloads" menu, download the Python 3.5.0 package (python-3.5.0-macosx10.6.pkg) or later.

2. Open the downloaded file to install it.

3. If you are a homebrew fan, you can install it using this brew command: ```brew install python3```

4. To install homebrew package manager, see: [brew.sh](http://brew.sh/)

##### Windows

Download the latest build (pywin32-220.win-amd64-py3.5.exe is the latest build as of this writing) from  [here](https://sourceforge.net/projects/pywin32/files/pywin32/Build%20220/) and run the downloaded executable.

### Setup Charm-Crypto

Indy-client requires anonymous credentials library which requires a cryptographic library.
The default configuration includes an example that uses Charm-Crypto framework.
You can install it as described in [Anonymous Credentials](https://github.com/evernym/anoncreds) repository 
(in particular, running `setup-charm.sh`).

As an alternative, there is a prepared deb packages which can be installed on Ubuntu:
```
sudo echo "deb http://us.archive.ubuntu.com/ubuntu xenial main universe" >> /etc/apt/sources.list
sudo echo "deb https://repo.sovrin.org/deb xenial stable" >> /etc/apt/sources.list
sudo apt-get update
sudo apt-get install python3-charm-crypto
```   

### Setup Libsodium

Indy also depends on libsodium, an awesome crypto library. These need to be installed separately.

##### Ubuntu 

1. We need to install libsodium with the package manager. This typically requires a package repo that's not active by default. Inspect ```/etc/apt/sources.list``` file with your favorite editor (using sudo). On ubuntu 16, you are looking for a line that says ```deb http://us.archive.ubuntu.com/ubuntu xenial main universe```. On ubuntu 14, look for or add: ```deb http://ppa.launchpad.net/chris-lea/libsodium/ubuntu trusty main``` and ```deb-src http://ppa.launchpad.net/chris-lea/libsodium/ubuntu trusty main```.

1. Run ```sudo apt-get update```. On ubuntu 14, if you get a GPG error about public key not available, run this command and then, after, retry apt-get update: ```sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys B9316A7BC7917B12```

1. Install libsodium; the version depends on your distro version. On Ubuntu 14, run ```sudo apt-get install libsodium13```; on Ubuntu 16, run ```sudo apt-get install libsodium18```

##### CentOS/Redhat

Run ```sudo yum install libsodium-devel```

##### Mac

Once you have homebrew installed, run ```brew install libsodium``` to install libsodium.

##### Windows

1. Go to https://download.libsodium.org/libsodium/releases/ and download the latest libsodium package (libsodium-1.0.8-mingw.tar.gz is the latest version as of this writing)

1. When you extract the contents of the downloaded tar file, you will see 2 folders with the names libsodium-win32 and libsodium-win64.

1. As the name suggests, use the libsodium-win32 if you are using 32-bit machine or libsodium-win64 if you are using a 64-bit operating system.

1. Copy the libsodium-x.dll from libsodium-win32\bin or libsodium-win64\bin to C:\Windows\System or System32 and rename it to libsodium.dll.


### Setup Indy-Crypto

Indy depends on [Indy-Crypto](https://github.com/hyperledger/indy-crypto).

There is a deb package of libindy-crypto that can be used on Ubuntu:
```
sudo echo "deb http://us.archive.ubuntu.com/ubuntu xenial main universe" >> /etc/apt/sources.list
sudo echo "deb https://repo.sovrin.org/deb xenial stable" >> /etc/apt/sources.list
sudo apt-get update
sudo apt-get install libindy-crypto
```

See [Indy-Crypto](https://github.com/hyperledger/indy-crypto) on how it can be installed on other platforms.

### Using a virtual environment (recommended)

We recommend creating a new Python virtual environment for trying out Indy.
A virtual environment is a Python environment which is isolated from the
system's default Python environment (you can change that) and any other
virtual environment you create. 

You can create a new virtual environment by:
```
virtualenv -p python3.5 <name of virtual environment>
```

And activate it by:

```
source <name of virtual environment>/bin/activate
```

### Installing code and running tests

Activate the virtual environment.

Navigate to the root directory of the source (for each project) and install required packages by
```
pip install -e .
```
If you are working with both indy-plenum and indy-node, then please make sure that both projects are installed with -e option,
and not from pypi (have a look at the sequence at `init-dev-project.sh`) 

Run tests by
```
python setup.py pytest
```