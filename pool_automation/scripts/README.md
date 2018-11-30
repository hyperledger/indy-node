# Helper scripts for Pool Automation Ansible roles

## Quickstart

- `namespace-config.py`: helps to create inventory directory with group variables
   that override Ansible Roles' defaults. The inventory directory then might be
   passed either to [Ansible command line tools][2aceed7f] or
   [molecule][1d2f4724].

  [2aceed7f]: https://docs.ansible.com/ansible/latest/user_guide/command_line_tools.html "ansible tools"
  [1d2f4724]: https://molecule.readthedocs.io/en/latest/index.html "molecule"

## Scripts

### namespace-config.py

Used to create inventory directory with user specified values for group
variables to use in Ansible roles.

The tool explores default values for each role it found and provides
command line API to override them.

The tool creates directory with the structure acceptable for Ansible inventory
directories as declared in [Working With Inventory](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html#splitting-out-host-and-group-specific-data). Also it adds an inventory file for
`localhost` to make its specification explicit.

```shell
inventory-dir/
└── group_vars
|   └── all
|       ├── <role-name1>_config.yml
|       ...
└── localhost.yml
```

So it is possible to place your inventory file(s) here (e.g. `inventory-dir/hosts`)
and pass either the whole directory or an inventory file to [Ansible command line tools][2aceed7f].

Also you may pass the `inventory-dir/group_vars` to molecule's provisioner
as a link as described [here](https://molecule.readthedocs.io/en/latest/configuration.html#provisioner).

### Requirements

- Python 2

### Environment variables

- `ANSIBLE_PROJECT_DIR` if defined used by the tool as a directory to search
  for roles. Otherwise (by default) the tool searches for roles in its parent
  directory.

### Command line API

Please refer to `namespace-config.py --help` for the detailed information
regarding available arguments.
