# Dev Setup

The preferred method of setting up the development environment is to use the **devcontainers**.
All configuration files for VSCode and [Gitpod](https://gitpod.io) are already placed in this repository.
If you are new to the concept of devcontainers in combination with VSCode [here](https://code.visualstudio.com/docs/remote/containers) is a good article about it.

Simply clone this repository and VSCode will most likely ask you to open it in the devcontainer, if you have the correct extension("ms-vscode-remote.remote-containers") installed.
If VSCode didn't ask to open it, open the command palette and use the `Remote-Containers: Rebuild and Reopen in Container` command.

If you want to use Gitpod simply use this [link](https://gitpod.io/#https://github.com/hyperledger/indy-node/tree/main)
or if you want to work with your fork, prefix the entire URL of your branch with  `gitpod.io/#` so that it looks like `https://gitpod.io/#https://github.com/hyperledger/indy-node/tree/main`.

**Note**: Be aware that the config files for Gitpod and VSCode are currently only used in the `main` branch!

## Using a virtual environment (recommended)

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

Optionally, you can install virtual environment wrapper as follows:
```
pip3 install virtualenvwrapper
echo '' >> ~/.bashrc
echo '# Python virtual environment wrapper' >> ~/.bashrc
echo 'export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3' >> ~/.bashrc
echo 'export WORKON_HOME=$HOME/.virtualenvs' >> ~/.bashrc
echo 'source /usr/local/bin/virtualenvwrapper.sh' >> ~/.bashrc
source ~/.bashrc
```
It allows to create a new virtual environment and activate it by using
```
mkvirtualenv -p python3.5 <env_name>
workon <env_name>
```


### Installing code and running tests

Activate the virtual environment.

Navigate to the root directory of the source (for each project) and install required packages by
```
pip install -e .[tests]
```
If you are working with both indy-plenum and indy-node, then please make sure that both projects are installed with -e option,
and not from pypi (have a look at the sequence at `init-dev-project.sh`).

Go to the folder with tests (either `indy-plenum`, `indy-node/indy_node`, `indy-node/indy_client` or `indy-node/indy_common`)
and run tests
```
pytest .
```
