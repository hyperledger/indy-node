# Setting Up a Test Indy Network in VMs

**WARNING**: This guideline assumes using of a deprecated CLI and deprecated Getting Started Guide.
Please have a look at [new client from SDK](https://github.com/hyperledger/indy-sdk/tree/master/cli) and new [Getting Started Guide](https://github.com/hyperledger/indy-sdk/blob/master/doc/getting-started/getting-started.md) instead.

When you're finished working through this document, you will be able to proceed through to the [*Getting
Started Guide*](../../../../getting-started.md) or if you would like, you may continue setting up an actual Developer Environment connected to a sandbox by following these [instructions](https://github.com/hyperledger/indy-node/blob/master/environment/vagrant/sandbox/DevelopmentEnvironment/Virtualbox/Vagrantfile).

This document will guide you in configuring a private network of Indy
validator nodes for testing and learning about Indy.  Additional servers
acting as Indy agents can also be provisioned on an ad-hoc basis, using this
framework.  Using this guide, VirtualBox VMs will be used as the basis for
creating a four-Validator network appropriate for completing the [*Getting
Started Guide*](../../../../getting-started.md)
and for other purposes.

### Assumptions

These instructions assume that you have an Internet connection, and are using a
computer with ample memory, CPU cores, and storage available.  A MacBook Pro
was used while writing this, but it should be easily adapted to other capable
computers.

Also, be aware that if during this process, you close out one agent or the CLI before instructed to, it may effect the performance and behavior of the other terminals you're working with. If you find that relaunching the terminal and reaccessing the CLI or the specific agent you closed does not fix the problem, you'll need to essentially start over with this process, which may be more time consuming than you originally planned.

It is best to work through this slowly and carefully. In the past, others have made errors during this process and have found that starting over completely was the only way to "fix it". If this process is not done correctly, you will not be able to run through the "Getting Started Guide" successfully.


### Installing VirtualBox

VirtualBox is a (FREE!) hypervisor technology similar to VMware's ESX that runs
on OSX, Linux and Windows PCs.  

* [Download VirtualBox](https://www.virtualbox.org/wiki/Downloads) and install
  it using the normal procedures for your OS.

### Install Vagrant

Vagrant is a (FREE!) scriptable orchestrator for provisioning VMs with
VirtualBox, ESX, AWS, and others.  We will be using it to run scripts provided
to you for creating VirtualBox VMs that will be our Indy validator and agent
nodes.  In addition to controlling VM provisioning, the Vagrant script will
remotely execute a configuration script on each node.  You will also be able to
use Vagrant commands to ssh login to the nodes, and to halt them or even to
destroy them when you are done. [Vagrant Command
Help](https://www.vagrantup.com/docs/cli/)

* [Download Vagrant](https://www.vagrantup.com/downloads.html) and install it
  using the normal procedures for your OS.
* run this command from a terminal window:
  ```sh
  $ vagrant box add bento/ubuntu-16.04
  ```
This downloads a Vagrant "box" for Ubuntu 16.04 (LTS) onto your PC.  Think of
your "box" as an VM image, similar to an AWS AMI or a VMware OVA.

> **Tip:** Try this if you get the error "The box 'bento/ubuntu-16.04' could not be found"
>   * `git clone https://github.com/chef/bento`
>   * `cd bento/ubuntu`
>   * `packer build ubuntu-16.04-amd64.json` # adjust for your environment
>   * `vagrant box add ../builds/ubuntu-16.04.virtualbox.box --name bento/ubuntu-16.04`

#### Warning

As of this writing Vagrant instructions do not work on a host ubuntu system due to a known vagrant issue found here: https://github.com/hashicorp/vagrant/issues/7155
.
## Download Vagrant script and bash scripts

Scripts to spin up Indy validator and agent nodes are available on github, in
the same location as this document.  If you have not already done so, install
git on your machine, then clone the repository to your local machine.  This is
the quickest way to get all the necessary files (plus more).  Then navigate to the
directory containing the scripts.

```sh
$ git clone https://github.com/hyperledger/indy-node.git
$ cd indy-node/environment/vagrant/training/vb-multi-vm
$ git checkout stable
```

At this point, you have all the artifacts necessary to create an Indy cluster
on VMs in your PC. Next, we will proceed to set up the cluster.

## Set Up Cluster of Indy Validator Nodes

The file that you see in the current directory, called "Vagrantfile", contains
the instructions that Vagrant will follow to command VirtualBox to provision
your VMs.  In addition, it instructs Vagrant to execute a bash file called
scripts/validator.sh on each of the validator VMs to install and configure the
required validator software.  It also has instructions for provisioning of
three agent VMs and one for use as a CLI client, with the required bash
configuration file for that purpose.

The script assumes that a 10.20.30.00/24 virtual network can be created in your
PC without conflicting with your external network configuration.  The addresses
of the VMs that will be provisioned will be taken from this network's address
range. It assumes that you are in the US:Mountain timezone.  These
settings, and more, can be changed in the Vagrantfile using a text editor.  You
may be able to run this script as-is, or you may want to:

* Change the timezone. For a list of candidates, refer to `/usr/share/zoneinfo`
  on an Ubuntu system.
* Change the IP addresses of the VMs
  * Change the Vagrantfile in each place that an IP address is designated for a
    validator or an agent
  * Change the list of validator IP addresses on line 48 of
    `scripts/validator.sh` accordingly
  * Likewise, change the list of validator IP addresses on line 42 of
    `scripts/agent.sh`
  * Change the IP addresses in the template hosts file at etc/hosts

After the configuration file has the correct settings, provision your
validator and CLI client nodes:

```sh
$ vagrant up
```

> **Note:** You will still need to be in this same directory (indy-node/environment/vagrant/training/vb-multi-vm) in order to run the above command. Also, you must wait until this process of "vagrant up" is complete prior to proceeding with the instructions below. If you attempt to proceed with the instructions below, it will cause error later in the process.

This command will take several minutes to complete, as each VM is provisioned
and its validator.sh script is executed.  After provisioning, each of the validator nodes
automatically joins the Indy validator cluster.  

> **Tip:** It may be instructive to examine the scripts/validator.sh file to see
> the steps taken to install, configure, and run the validator nodes.

If you will be using these VMs to run the Getting Started Guide, you will need additional VMs to run your agent nodes. In this case, run this to provision these as well:

```sh
$ vagrant up agent01 agent02 agent03
```
Alternatively, if you want to work with the libindy SDK (not the Getting Started Guide), you can bring up one or two nodes for this experimentation or development:

```sh
$ vagrant up libindy01 libindy02
```

If at any time you need to log in to a validator or other of these nodes to check logs or do other
administrative tasks, you can ssh into it easily.  For example, to access the
first validator node, which has the name `validator01`, go into the directory
with your Vagrantfile script and enter the following on the command line.

```sh
$ vagrant ssh validator01
```

Login is seamless since Vagrant automatically generates and configures an ssh
key pair for access.

## Setting Up a CLI Client and Configuring the Agents in the Indy Cluster

Before you begin, make sure you have four console windows open, one for the CLI and one each for the other three VMs.

You will need to have a term session to ssh into one of these nodes, which will
be used as an interactive CLI client.  With this you will be able to interact
with the Indy validator cluster and with the agents.  If you are doing the
Getting Started Guide, two roles will be performed using the CLI client.
First, you will use it in the role of a Steward, a privileged user who
will be used to register and configure the agents on the Indy validator
cluster that we have set up.  Later, you will use the CLI client in the role of
Alice, a user who has various interactions with the agents that are facilitated
by Indy.

In a term window, you will now ssh into `cli01`, bring up the CLI, and
configure the CLI to communicate with the "test" Indy validator cluster that
we have configured here.

```sh
$ vagrant ssh cli01
vagrant@cli01:~$ indy
indy> connect sandbox
```

The next task is to register the agents that we will be using with Indy.  We
must do this before starting the agent processes in the other nodes, since
these processes expect to be registered in the Indy cluster before starting. In order to
do the registration, we must be able to authenticate to the indy cluster as a Steward.
In our test cluster, there is a pre-configured user called `Steward1` with a
known key that we are able to use.  In the CLI, type:

```
indy@sandbox> new key with seed 000000000000000000000000Steward1
```

Now that the CLI client can authenticate as the `Steward1` user, we can put
transactions into the Indy validator cluster that will register each agent
and establish its endpoint attribute.  To register the agents used in the
Getting Started Guide, first, as the Steward, add each of the three agent's
Endorser to the ledger.:

```
indy@sandbox> send NYM dest=ULtgFQJe6bjiFbs7ke3NJD role=ENDORSER verkey=~5kh3FB4H3NKq7tUDqeqHc1
indy@sandbox> send NYM dest=CzkavE58zgX7rUMrzSinLr role=ENDORSER verkey=~WjXEvZ9xj4Tz9sLtzf7HVP
indy@sandbox> send NYM dest=H2aKRiDeq8aLZSydQMDbtf role=ENDORSER verkey=~3sphzTb2itL2mwSeJ1Ji28
```

In the first of the above commands, `~5kh3FB4H3NKq7tUDqeqHc1` is the
verification key of the "Faber College" Endorser.  A corresponding private
key is retained by the agent process. `ULtgFQJe6bjiFbs7ke3NJD` is the "Faber
College" Endorser ID.  The other two lines put the Endorsers for "Acme
Corp" and "Thrift Bank" onto the ledger as well.

Next, we provide information on the nodes that these Endorsers will use to
interact with clients.  If necessary, replace the IP addresses and ports in
these commands with what you are using.  Since only the Endorser can modify
his information on the ledger, we must assume the proper identity before
posting each transaction.

```
indy@sandbox> new key with seed Faber000000000000000000000000000
indy@sandbox> send ATTRIB dest=ULtgFQJe6bjiFbs7ke3NJD raw={"endpoint": {"ha": "10.20.30.101:5555", "pubkey": "5hmMA64DDQz5NzGJNVtRzNwpkZxktNQds21q3Wxxa62z"}}
indy@sandbox> new key with seed Acme0000000000000000000000000000
indy@sandbox> send ATTRIB dest=CzkavE58zgX7rUMrzSinLr raw={"endpoint": {"ha": "10.20.30.102:6666", "pubkey": "C5eqjU7NMVMGGfGfx2ubvX5H9X346bQt5qeziVAo3naQ"}}
indy@sandbox> new key with seed Thrift00000000000000000000000000
indy@sandbox> send ATTRIB dest=H2aKRiDeq8aLZSydQMDbtf raw={"endpoint": {"ha": "10.20.30.103:7777", "pubkey": "AGBjYvyM3SFnoiDGAEzkSLHvqyzVkXeMZfKDvdpEsC2x"}}
```

### Starting the Agent Processes

Now that the agents are registered with the Indy cluster, the agent processes
can be started on their respective nodes.  You will need to `vagrant ssh` into
each one of them and start the agent process manually. Remember, you will need to do each one in its own separate terminal. If you are setting up
to run through the getting started guide, bring up a terminal, go into the
directory with your `Vagrantfile` script, and execute the following to start up
the "Faber College" agent process.

````sh
$ vagrant ssh agent01
vagrant@agent01:~$ python /usr/local/lib/python3.5/dist-packages/indy_client/test/agent/faber.py  --port 5555 --network <network_name>
````

You will see logging output to the screen.  In another term window (or tab),
ssh into agent02 and bring up the "Acme Corp" agent process:

````sh
$ vagrant ssh agent02
vagrant@agent02:~$ python /usr/local/lib/python3.5/dist-packages/indy_client/test/agent/acme.py  --port 6666 --network <network_name>
````

In another term window (or tab), ssh into agent03 and bring up the "Thrift
Bank" agent process:

```sh
$ vagrant ssh agent03
vagrant@agent03:~$ python /usr/local/lib/python3.5/dist-packages/indy_client/test/agent/thrift.py  --port 7777 --network <network_name>
```

Congratulations!  Your Indy four-validator cluster, along with agent nodes as
desired, is complete.  Now, in the CLI client on `cli01`, type quit to exit the
CLI.  If you are doing the Getting Started Guide you are ready to proceed,
using `cli01` for the interactive 'Alice' client.  In `cli01`, type indy to
once again to bring up the CLI prompt, and continue with the guide.

```
vagrant@cli01:~$ indy
Loading module /usr/local/lib/python3.5/dist-packages/config/config-crypto-example1.py
Module loaded.

Indy-CLI (c) 2017 Evernym, Inc.
Type 'help' for more information.
Running Indy 1.2.50

indy>
```
