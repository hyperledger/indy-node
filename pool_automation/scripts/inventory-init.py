#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
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


def _init_roles_defaults():
    proj_dir = os.getenv('ANSIBLE_PROJECT_DIR')
    if not proj_dir:
        script_path = os.path.abspath(getsourcefile(lambda: 0))
        proj_dir = os.path.abspath(os.path.join(os.path.dirname(script_path), '..'))
    else:
        proj_dir = os.path.abspath(proj_dir)

    roles = {os.path.basename(r): {'path': r} for r in glob.iglob("{}/roles/*".format(proj_dir))}

    if not roles:
        logger.error("No roles are found in {}".format(proj_dir))
        raise RuntimeError("No roles are found in {}".format(proj_dir))

    for role, params in roles.iteritems():
        _fpath = "{}/defaults/main.yml".format(params['path'])
        try:
            with open(_fpath, 'r') as _f:
                roles[role]['defaults'] = yaml.safe_load(_f)
        except IOError:
            logger.debug("Ignoring absense of the file {}".format(_fpath))

    return roles


def _clear_logging():
    for handler in logging.root.handlers[:]:
        handler.flush()
        logging.root.removeHandler(handler)
        handler.close()


def _set_logging(logconfig_path=None):
    _clear_logging()
    if logconfig_path:
        with open(logconfig_path, "rb") as f:
            logging.config.dictConfig(
                json.load(f, object_pairs_hook=OrderedDict)
            )
    else:
        logging.basicConfig(level=DEF_LOGLEVEL, format=DEF_LOGGING_FORMAT)


def _parse_args(roles):
    parser = argparse.ArgumentParser(
        description="Inventory Init Tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('inventory-dir',
                        help='path to inventory directory')

    for role, params in roles.iteritems():
        if 'defaults' not in params:
            continue

        _group = parser.add_argument_group(
            "{} vars".format(role)
        )
        for p, d in params['defaults'].iteritems():
            _help_kwargs = {'metavar': "{}".format(type(d).__name__).upper()}
            # TODO smarter data types related routine:
            #   - dict: is it acutal case?
            #   - be generic: shouldn't have any role's specific things
            if type(d) is list:
                _help_kwargs['nargs'] = '+'
                _help_kwargs['metavar'] = 'ITEM'
            elif type(d) in (int, float):
                _help_kwargs['type'] = type(d)

            _group.add_argument("--{}.{}".format(role, p), **_help_kwargs)

    parser.add_argument("--logconfig", metavar="PATH", default=None,
                        help=("Path to json-formatted logging configuration"
                              " file, if not defined the one the basic"
                              " one will be used"))

    parser.add_argument("--show-defaults", action="store_true",
                        help="Show defaults and exit")

    return vars(parser.parse_args())


def _dump_defaults(roles):
    for role, params in roles.iteritems():
        if 'defaults' in params:
            print(role.upper())
            print(yaml.safe_dump(params['defaults'], default_flow_style=False))


def _specify_localhost(inventory_dir):
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

    with open(os.path.join(inventory_dir, 'localhost.yml'), "w") as _f:
        _f.write('---\n')
        yaml.safe_dump(localhost_spec, _f, default_flow_style=False)


def main():

    _set_logging()

    roles = _init_roles_defaults()

    args = _parse_args(roles)

    # output default api settings

    # config logging
    if args['logconfig'] is not None:
        _set_logging(args['logconfig'])

    logger.debug("Cmd line arguments: {}".format(args))

    if args["show_defaults"]:
        _dump_defaults(roles)
        exit(0)

    # create inventory dir hierarchy
    group_vars_dir = "{}/group_vars/all".format(args['inventory-dir'])
    if not os.path.isdir(group_vars_dir):
        os.makedirs(group_vars_dir)

    # dump configs
    # TODO consider to use Ansible's 'to_nice_yaml' from
    #      ansible.plugins.filter.core.py BUT it's not a public API
    with open("{}/config.yml".format(group_vars_dir), "w") as _f:
        _f.write('---\n')

        for role, params in roles.iteritems():
            if 'defaults' not in params:
                continue

            _f.write("\n# {0} {1} {0}\n".format('='*20, role))
            # construct user specified config parameters
            config = {}
            for _p in params['defaults'].keys():
                _arg_name = "{}.{}".format(role, _p)
                if args.get(_arg_name):
                    config[_p] = args[_arg_name]

            if config:
                yaml.safe_dump(config, _f, default_flow_style=False)

            _s = yaml.safe_dump(params['defaults'], default_flow_style=False)
            _f.write(''.join(["\n# defaults\n\n"] + ["#{}".format(_l) for _l in _s.splitlines(True)]))

    # add inventory file for localhost
    _specify_localhost(args['inventory-dir'])


if __name__ == "__main__":
    sys.exit(main())
