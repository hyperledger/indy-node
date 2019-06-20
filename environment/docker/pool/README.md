# Prerequisites
* Docker
* Current user added to 'docker' group (not needed for all environments)
* macOS users will need to install an up to date version of sed using Homebrew `brew install gnu-sed`

# Start pool
```
./pool_start.sh [number of nodes in pool] [IP addresses of nodes] [number of clients] [port for the first node]
```
Defaults:
* Number of nodes is 4
* IP addresses are generated consequently starting from 10.0.0.2
** Format: 10.0.0.2,10.0.0.3,10.0.0.4,10.0.0.5
* Number of clients is 10
* Ports are generated consequently starting from 9701

# Stop pool
```
./pool_stop.sh [file with pool data] [pool network name]
```
Defaults:
* File is pool_data
* Network name is pool-network

# Running on Windows using git bash

Using the git bash shell is a productive command line for those familiar with Unix/Linux to run applications/environments on Windows. However, git bash can create problems with pathnames, and does so with this application. Specifcally, by default git bash converts absolute path names to a Windows equivalent path name (e.g. C:\\...), which is helpful if it is expected by an app, but not always - and rarely with Docker.  In particular, [it's not helpful with Docker](https://github.com/moby/moby/issues/24029) volume mounting on docker run and build commands. The Indy test scripts - client_build.sh, node_build.sh, client_start.sh and node_start.sh are all affected by this. When just run, docker build/run commands error off with messages like:

```
C:\Program Files\Docker\Docker\Resources\bin\docker.exe: Error response from daemon: invalid bind mount spec "/C/Program Files/Git/sys/fs/cgroup;C:\\Program Files\\Git\\sys\\fs\\cgroup;ro": invalid volume specification: '/C/Program Files/Git/sys/fs/cgroup;C:\Program Files\Git\sys\fs\cgroup;ro': invalid mount config for type "bind": invalid mount path: '\Program Files\Git\sys\fs\cgroup;ro' mount path must be absolute.
```

The easiest way to prevent pathname expansion is to preface the pool and client commands with *MSYS_NO_PATHCONV=1*, for example:

```
MSYS_NO_PATHCONV=1 ./pool_start.sh
```

Alternatively, you can edit the scripts and on the docker run and build scripts, change leading slashes (/) in pathnames to double slashes (//) on -v (volume mount) parameters.
