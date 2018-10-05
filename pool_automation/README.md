# Ansible roles to install and manage pool of Indy Node

## Quickstart

- Make sure you have `AWS_ACCESS_KEY` and `AWS_SECRET_KEY` in your environment
  with corresponding AWS access keys.
- Run `ansible-playbook pool_create.yml` - this will create 4 EC2 instances
  and `test_nodes` directory with inventory and SSH keys.
- Run `ansible-playbook -i test_nodes/hosts pool_install.yml` - this will
  install and configure Indy Node pool on previously created EC2 instances.
- Run `ssh -F test_nodes/ssh_config test_node_1` to login to first node
  and take a look around.
- Run `ansible-playbook pool_destroy.yml` - this will terminate previously
  created AWS EC2 instances and clear `config_pool` and `inventory_pool` files.


## Roles

### aws_manage

Used to manage number of AWS instances.

Parameters:
- _instance_count_: number of instances in pool (provide 0 to destroy)
- _aws_type_ (t2.micro): type of instances
- _aws_region_ (eu-central-1): region of instances
- _tag_namespace_ (test): namespace of created instances
- _tag_role_ (default): role of created instances

Todos:
- allow created instances span all regions
- extract key generation and inventory export to separate role
- make inventory span separate roles in namespace
- more tests


### common

Installs python and sovrin GPG keys.


### node_install

Adds sovrin repository and installs Indy Node.

Parameters:
- _channel_ (master): which release channel to use (master/rc/stable)
- _indy_node_ver_
- _indy_plenum_ver_
- _python_indy_crypto_ver_
- _libindy_crypto_ver_

Todos:
- allow providing only _indy_node_ver_
- remove unused repositories when switching channels


### pool_install

Configures Indy Node pool.


## Development

Install system packages:
- vagrant
- python 2.7 or 3.6, including dev package

Install virtualenv packages:
- molecule
- testinfra
- python-vagrant
- boto
- boto3

In order to test role go to directory with role (for example 
`roles/pool_install`) and run `molecule test --all`.

To speed up development following workflow is recommended:
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
