# Ansible roles to install and manage pool of Indy Node

## Quickstart

- Make sure you have [AWS CLI][f681b33b] installed and configured.
- [Install](#installation) requirements
- Run `ansible-playbook pool_create.yml` - this will create 4 EC2 instances
  and `test_nodes` directory with inventory and SSH keys.
- Run `ansible-playbook -i test_nodes/hosts pool.yml` - this will
  install and configure Indy Node pool on previously created EC2 instances.
- Run `ssh -F test_nodes/ssh_config test_node_1` to login to first node
  and take a look around.
- Run `ansible-playbook destroy.nodes.yml` - this will terminate previously
  created AWS EC2 instances and clear `config_pool` and `inventory_pool` files.

  [f681b33b]: https://aws.amazon.com/cli/ "aws cli"

## Installation

- python 2.7 or 3.6
- required packages: `pip install -r requirements.txt`, options:
  - (recommended) inside python virtual environment
  - with `--user` inside user Python install directory
  - (not recommended) globally using `sudo`

## Roles

### aws_manage

Used to manage number of AWS instances.

Parameters:
- _instance_count_: number of instances in pool (provide 0 to destroy)
- _aws_ec2_type_ (t2.micro): type of instances
- _aws_region_ (eu-central-1): region of instances
- _aws_tag_project_ (PoolAutomation): project name for created instances
- _aws_tag_namespace_ (test): namespace of created instances
- _aws_tag_group_ (default): ansible inventory group of created instances

Todos:
- extract key generation and inventory export to separate role
- make inventory span separate roles in namespace
- more tests


### ansible_bootstrap

Installs python and sudo.


### indy_node

Adds sovrin repository and installs and configures Indy Node.

Parameters:
- _indy_node_channel_ (master): which release channel to use (master/rc/stable)
- _indy_node_ver_
- _indy_plenum_ver_
- _python_indy_crypto_ver_
- _libindy_crypto_ver_

Todos:
- allow providing only _indy_node_ver_
- remove unused repositories when switching channels


## Scripts

The directory [scripts](scripts) includes helper scripts. Please refer to [scripts/README.md](scripts/README.md) for more details.

## Development

Install system packages:
- vagrant
- python 2.7 or 3.6, including dev package

Install python packages:

`pip install -r requirements-dev.txt`

Default development workflow would be:
- `molecule lint`
- `molecule converge`
- `molecule verify`
- `molecule destroy`

When you are ready you can run aggregative command `molecule test`.

### Scenarios

By default scenarios based on `docker` are used. Also `vagrant` scenarios are available
and might be run like `molecule <command> -s vagrant`.

In order to test all scenarios for some role go to a directory with the role (for example
`roles/indy_node`) and run `molecule test --all`.

#### Vagrant scenarios specific

To speed up development and testing on vagrant VMs following workflow is recommended:
- After each change run `molecule lint`. This will quickly show some
  style recommendations and probably highlight some stupid mistakes.
- When lint is satisfied run `molecule converge`. This will spin up
  virtual machines (if neccessary) and run default playbook. This
  could be slow operation when running for the first time, but
  subsequent runs are much faster.
- When converge finishes without errors run `molecule verify`. This
  will start tests.
- Do more changes, running this lint-converge-verify sequence.
- When done (or there is suspicion that VM state gone very bad) run
  `molecule destroy`, this will destroy virtual machines.
- When virtual machines are running it's possible to login to them
  using `molecule login --host name`