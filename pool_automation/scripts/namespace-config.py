#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
from inspect import getsourcefile
import json
import glob
import argparse
import yaml
from collections import OrderedDict
import logging
import logging.config

logger = logging.getLogger(__name__)

DEF_LOGGING_FORMAT = ("%(asctime)s - %(name)s - %(levelname)s - "
                      "[%(filename)s:%(lineno)d]: %(message)s")
DEF_LOGLEVEL = logging.INFO

DEFAULT_INV_SCHEME = """
localhosts.yml:
  all:
    children:
      localhosts:
        vars:
          ansible_connection: local
          ansible_python_interpreter: '{{ ansible_playbook_python }}'
        hosts:
          localhost:
          aws_clients_provisioner:
          aws_nodes_provisioner:

host_vars:
  aws_nodes_provisioner:
    - aws_manage
  aws_clients_provisioner:
    - aws_manage

group_vars:
  all:
    - ansible_bootstrap
  localhosts:
    - aws_manage
  nodes:
    - indy_node
    - plugins
  clients:
    - indy_cli
    - perf_scripts
    - plugins
"""


class Role(object):

    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)

        self.defaults = {}
        self.defaults_path = "{}/defaults/main.yml".format(self.path)

        self._load_defaults()

    def _load_defaults(self):
        try:
            with open(self.defaults_path, 'r') as _f:
                self.defaults = yaml.safe_load(_f)
        except IOError:
            logger.debug("Ignoring absense of the file {}".format(self.defaults_path))


class RoleRef(object):
    def __init__(self, role):
        self.role = role
        self.vars = {}

    def set_vars(self, role_vars):
        # treat role's defaults as a collection of only possible vars
        if self.defaults:
            self.vars.update(
                {k: v for k, v in role_vars.iteritems() if k in self.defaults})

    @property
    def name(self):
        return self.role.name

    @property
    def defaults(self):
        return self.role.defaults


class InvBase(object):
    def __init__(self, inv_dir, name, *rel_dirs):
        if not re.search(r'\.(yml|yaml)$', name):
            name = "{}.yml".format(name)
        self.name = name
        self.path = os.path.join(os.path.join(inv_dir, *rel_dirs), name)

    def _dump(self, stream):
        raise NotImplementedError

    def dump(self):
        with open(self.path, "w") as _f:
            _f.write('---\n')
            self._dump(_f)
            _f.write('...\n')


class Inv(InvBase):
    def __init__(self, inv_dir, name, content):
        self.content = content
        super(Inv, self).__init__(inv_dir, name)

    def _dump(self, stream):
        stream.write(yaml.safe_dump(self.content, default_flow_style=False))


class InvVars(InvBase):

    def __init__(self, inv_dir, vars_name, name, roles_refs):
        self.roles_refs = roles_refs
        super(InvVars, self).__init__(inv_dir, name, vars_name)

    def _dump(self, stream):
        for role_ref in self.roles_refs:
            stream.write("\n# {0} {1} {0}\n".format('=' * 20, role_ref.name))

            if role_ref.vars:
                stream.write(yaml.safe_dump(role_ref.vars, default_flow_style=False))

            if role_ref.defaults:
                _s = yaml.safe_dump(role_ref.defaults, default_flow_style=False)
                stream.write(''.join(["\n# defaults\n\n"] +
                             ["#{}".format(_l) for _l in _s.splitlines(True)]))


def _load_roles():
    proj_dir = os.getenv('ANSIBLE_PROJECT_DIR')
    if not proj_dir:
        script_path = os.path.abspath(getsourcefile(lambda: 0))
        proj_dir = os.path.abspath(os.path.join(os.path.dirname(script_path), '..'))
    else:
        proj_dir = os.path.abspath(proj_dir)

    roles = [Role(r) for r in glob.iglob("{}/roles/*".format(proj_dir))]

    if not roles:
        logger.error("No roles are found in {}".format(proj_dir))
        raise RuntimeError("No roles are found in {}".format(proj_dir))

    return {r.name: r for r in roles}


def _load_inv_scheme():
    inv_scheme_path = os.getenv('ANSIBLE_INV_SCHEME')
    if inv_scheme_path:
        with open(inv_scheme_path, 'r') as _f:
            return yaml.safe_load(_f)
    else:
        return yaml.safe_load(DEFAULT_INV_SCHEME)


def _reset_logging():
    for handler in logging.root.handlers[:]:
        handler.flush()
        logging.root.removeHandler(handler)
        handler.close()


def _set_logging(logconfig_path=None):
    _reset_logging()
    if logconfig_path:
        with open(logconfig_path, "rb") as f:
            logging.config.dictConfig(
                json.load(f, object_pairs_hook=OrderedDict)
            )
    else:
        logging.basicConfig(level=DEF_LOGLEVEL, format=DEF_LOGGING_FORMAT)


def _arg_name(var_name, arg_prefix=None):
    return "{}.{}".format(arg_prefix, var_name) if arg_prefix else var_name


def _parse_args(roles, inv_mode, inv_scheme=None):
    parser = argparse.ArgumentParser(
        description="Namespace Configuration Tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('namespace-dir',
                        help='path to namespace directory')

    parser.add_argument("--namespace-name", metavar="STR", default=None,
                        help=("Name of the namespace. "
                              "Default: basename of the 'namespace-dir'"))

    parser.add_argument("--inventory-name", metavar="STR", default='inventory',
                        help=("Name of the inventory directory inside "
                              "the 'namespace-dir'"))

    parser.add_argument("--logconfig", metavar="PATH", default=None,
                        help=("Path to json-formatted logging configuration"
                              " file, if not defined the basic"
                              " one will be used"))

    parser.add_argument("--show-defaults", action="store_true",
                        help="Show defaults and exit")

    def add_role_group(parent, role, arg_prefix=None, title=None, descr=None):

        if role.defaults is None:
            return

        _group = parent.add_argument_group(title, descr)
        for p, d in role.defaults.iteritems():
            _help_kwargs = {'metavar': "{}".format(type(d).__name__).upper()}
            if type(d) is list:
                _help_kwargs['nargs'] = '+'
                _help_kwargs['metavar'] = 'ITEM'
            elif type(d) is dict:
                _help_kwargs['metavar'] = 'JSON'
                _help_kwargs['type'] = json.loads
            elif type(d) in (int, float):
                _help_kwargs['type'] = type(d)

            _group.add_argument("--{}".format(_arg_name(p, arg_prefix)), **_help_kwargs)

    if inv_mode == 'plays':
        for inv, inv_spec in inv_scheme.iteritems():
            if inv not in ('host_vars', 'group_vars'):
                continue

            for inv_obj, role_names in inv_spec.iteritems():
                for role_name in role_names:
                    add_role_group(parser, roles[role_name], arg_prefix=inv_obj,
                                   title="'{}' {} vars for '{}' role"
                                         .format(inv_obj, inv.split('_')[0], roles[role_name].name))
    else:
        for role in roles.itervalues():
            add_role_group(parser, role, title="'{}' role vars".format(role.name))

    return vars(parser.parse_args())


def _dump_defaults(roles):
    for role in roles.itervalues():
        if role.defaults is not None:
            print(role.name.upper())
            print(yaml.safe_dump(role.defaults, default_flow_style=False))


def main():

    _set_logging()

    roles = _load_roles()
    inv_mode = os.getenv('ANSIBLE_INVENTORY_MODE', 'plays')
    inv_scheme = _load_inv_scheme() if inv_mode == 'plays' else None

    args = _parse_args(roles, inv_mode, inv_scheme)

    # config logging
    if args['logconfig'] is not None:
        _set_logging(args['logconfig'])

    logger.debug("Cmd line arguments: {}".format(args))

    if args["show_defaults"]:
        _dump_defaults(roles)
        exit(0)

    inv_dir = os.path.join(args['namespace-dir'], args['inventory_name'])
    namespace_name = (args['namespace_name'] if args['namespace_name']
                      else os.path.basename(args['namespace-dir']))

    # create inventory dir hierarchy
    for d in ('host_vars', 'group_vars'):
        _path = os.path.join(inv_dir, d)
        if not os.path.isdir(_path):
            os.makedirs(_path)

    def get_user_vars(role, arg_prefix=None):
        # construct user specified vars
        user_vars = {}
        for v_name in role.defaults.keys():
            arg_name = _arg_name(v_name, arg_prefix)
            if args.get(arg_name):
                user_vars[v_name] = args[arg_name]
        return user_vars

    namespace_spec = {
        'all': {
            'vars': {
                'namespace_dir': os.path.join('{{ inventory_dir }}', '..'),
                'namespace_name': namespace_name,
                'namespace_dir_relative': '..'
            }
        }
    }

    inventories = [Inv(inv_dir, 'namespace.yml', namespace_spec)]
    if inv_mode == 'plays':
        for inv, inv_spec in inv_scheme.iteritems():
            if inv in ('host_vars', 'group_vars'):
                for inv_obj, role_names in inv_spec.iteritems():
                    _roles = []
                    for role_name in role_names:
                        role_ref = RoleRef(roles[role_name])
                        role_ref.set_vars(get_user_vars(role_ref, inv_obj))
                        _roles.append(role_ref)
                    inventories.append(InvVars(inv_dir, inv, inv_obj, _roles))
            else:
                inventories.append(Inv(inv_dir, inv, inv_spec))
    else:  # role oriented logic
        localhost_spec = {
            'all': {
                'hosts': {
                    'localhost': {
                        'ansible_connection': 'local',
                        'ansible_python_interpreter': '{{ ansible_playbook_python }}'
                    }
                }
            }
        }
        inventories.append(Inv(inv_dir, 'localhost.yml', localhost_spec))
        _roles = []
        for role in roles.itervalues():
            role_ref = RoleRef(role)
            role_ref.set_vars(get_user_vars(role_ref))
            _roles.append(role_ref)
        inventories.append(InvVars(inv_dir, 'group_vars', 'all', _roles))

    for inv in inventories:
        inv.dump()


if __name__ == "__main__":
    main()
    sys.exit(0)
