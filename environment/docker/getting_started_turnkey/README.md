# Abstract

A turnkey, Docker-based sandbox that enables quick and easy exploration of Hyperledger Indy concepts. This devops repo can be used to gather hands-on experience of Indy basics using the scenarios outlined in the [Sovrin's Getting Started Guide](https://github.com/hyperledger/indy-node/blob/stable/getting-started.md).

## Quick Summary commands

With just four command lines executed you have the Indy Demo ready to use.

```
$ git clone https://github.com/hyperledger/indy-node.git
$ cd indy-node/environment/docker/getting_started_turnkey
$ make indy-base
$ make run-demo
```

# Indy Docker

A Docker file is provided that creates and configures Indy nodes and clients. The resulting Docker image can be used to instantiate the particants in the **Alice Demo** that are described in the [Sovrin's Getting Started Guide](https://github.com/hyperledger/indy-node/blob/stable/getting-started.md).

## Dependencies

While the Docker image that will be created below may run on many different versions of Docker, it was initially tested and verified on Docker v17.10.0-ce.  To see what version of Docker is currently installed on your system, run:

```
$ docker --version
```

Information on downloading and installing Docker for various platforms can be found [here](https://www.docker.com/get-docker).

## Step 1: Create the Indy Docker Image

Clone the **indy-node** repository.

```
$ git clone https://github.com/hyperledger/indy-node.git
```
   
Change to the cloned directory and use the **Makefile** target **indy-base** to create the **indy-base** Docker image.

```
$ cd indy-node/environment/docker/getting_started_turnkey
$ make indy-base
```

Now, you should have a **indy-base** Docker image available to run.

```
$ docker images
REPOSITORY              TAG                 IMAGE ID            CREATED             SIZE
indy-base               latest              0e5fe43800da        43 hours ago        1.09GB
```

## Step 2: Run the Alice Demo

You can set up and run the **Alice Demo** using the **indy-base** Docker image from Step 1.  In the cloned directory there is a **Makefile** that can be used to start and stop all of the Docker containers used for the demo.  

The **run-demo** target starts a four-node pool (Node1-Node4), sets up and runs the Faber, Acme and Thrift agents, and starts an Indy CLI.

```
$ make run-demo
```

The **Makefile** has a number of targets that perform many tasks. An attempt is made to determine the local IP address.  It can be checked using the **local** target.  If you want to use a different IP address, you can edit the Makefile and set the LOCAL variable.  

To see what your local address is you can run the command with just the **local** target.

```
$ make local 
```

After executing the **run-demo** target, you should have 8 Docker containers running.

```
$ docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                              NAMES    
e26633e1d1f9        indy-base           "/bin/bash -c '   ..."   10 seconds ago      Up 11 seconds                                          Indy
41e9fcc0733f        indy-base           "/bin/bash -c 'gen..."   11 seconds ago      Up 12 seconds       0.0.0.0:7777->7777/tcp             Thrift
287accdc16a2        indy-base           "/bin/bash -c 'gen..."   12 seconds ago      Up 12 seconds       0.0.0.0:6666->6666/tcp             Acme
5d13e6af5836        indy-base           "/bin/bash -c 'gen..."   13 seconds ago      Up 13 seconds       0.0.0.0:5555->5555/tcp             Faber
70126d9120f0        indy-base           "/bin/bash -c 'ini..."   13 seconds ago      Up 14 seconds       0.0.0.0:9707-9708->9707-9708/tcp   Node4
5305fcb69354        indy-base           "/bin/bash -c 'ini..."   14 seconds ago      Up 15 seconds       0.0.0.0:9705-9706->9705-9706/tcp   Node3
63932d40357e        indy-base           "/bin/bash -c 'ini..."   15 seconds ago      Up 15 seconds       0.0.0.0:9703-9704->9703-9704/tcp   Node2
7e9f2f93f41e        indy-base           "/bin/bash -c 'ini..."   15 seconds ago      Up 16 seconds       0.0.0.0:9701-9702->9701-9702/tcp   Node1
```

When the Indy container starts, it runs several Indy commands that set up the agents.  Once the agents are operational, you are at the **indy>** prompt and the demo environment is ready for use.  You can now follow the **Alice Demo** scenario.  

The following commands are from the demo script and can be used to test that the demo environment is working correctly.

```
indy@sandbox> prompt ALICE
ALICE@sandbox> new wallet Alice
ALICE@sandbox> show sample/faber-request.indy
ALICE@sandbox> load sample/faber-request.indy
ALICE@sandbox> show connection "Faber College"
ALICE@sandbox> accept request from "Faber College"
ALICE@sandbox> show claim Transcript
ALICE@sandbox> request claim Transcript
ALICE@sandbox> show claim Transcript
```

The entire **Alice Demo** can be run using the **run-alice** target.  This does everything that the **run-demo** target does, plus executes the remaining Indy commands to run the entire demo.  

You will be left at the **indy>** prompt, allowing you to explore additional commands.  To get a list of all Indy commands, enter **help**.  

The **exit** command will exit the Indy command prompt and leave you at the bash shell command line.  You can explore the file system or run the Indy command prompt again by typing **indy**.

There are several directories under **~/.indy-cli** that might be interesting to explore.  The network configuration is in the **~/.indy-cli/networks/sandbox** directory, and the wallets are in the **~/.indy-cli/wallets/sandbox** directory.


## Makefile Targets

The following **Makefile** targets can be used to start and stop the Docker containers and set up the demo environment used for the **Alice Demo**.

**indy-base**

* Create the Docker image that is used for both Indy nodes and clients.

**local**

* Find the local host IP address.

**run-demo**

* Start all Indy node, Indy agents and Indy CLI used for the **Alice Demo**.  This also automatically executes several Indy commands that set up the agents before leaving you at the **indy>** prompt.

**run-alice**

* Start all Indy node, Indy agents and Indy CLI used for the **Alice Demo**.  This also automatically executes all of the Indy commands that run the entire Alice demo before leaving you at the **indy>** prompt.

**indy-cli**

* Start a new Indy CLI client leaving you at the **indy>** prompt.

**stop**

* Stop all Docker containers used for the **Alice Demo**.

**start**

* Start all stopped Docker containers used for the **Alice Demo** that were stopped using the **stop** target.

**clean**

* Stop and remove all Docker containers used for the **Alice Demo**.

## Troubleshooting

Some failures running through the demo can be due to failure to contact the various service endpoints.  Verify the IP addresses that the makefile is using and edit the Makefile LOCAL variable as necessary.



## Using the Docker Image

The **indy-base** Docker image is used for both Indy nodes and clients.  

You can run the Docker image and interact with it using a bash shell.

```
$ docker run -it --rm indy-base /bin/bash
```

To start the Docker image as an Indy client:

```
$ docker run -it --rm indy-base /bin/bash
# indy
Loading module /usr/local/lib/python3.5/dist-packages/config/config-crypto-example1.py
Module loaded.

Indy-CLI (c) 2017 Evernym, Inc.
Type 'help' for more information.
Running Indy 1.2

indy> 
```

To start the docker image as an Indy node:

```
$ docker run -it --rm indy-base /bin/bash
# init_indy_keys --name Alpha
# start_indy_node Alpha 9701 9702
```

You can connect to an existing node:

```
$ docker exec -it Node1 /bin/bash
```

## Cleanup

To stop and remove the created Docker containers from your system:

```
$ make clean
```

To remove the Docker image from your system:

```
$ docker rmi indy-base
```

## Links

* [Getting Started with Indy](https://github.com/hyperledger/indy-node/blob/stable/getting-started.md)
* [Indy Node](https://github.com/hyperledger/indy-node)
* [Indy – Running the Getting Started tutorial locally](https://github.com/hyperledger/indy-node/blob/master/docs/indy-running-locally.md)
* [Create a Network and Start Nodes](https://github.com/hyperledger/indy-node/blob/master/docs/start-nodes.md)
