#! /usr/bin/env python3
import sys
import subprocess
import shutil
import codecs
import locale
import datetime
import os
import random
from typing import Tuple, Union, TypeVar, List, Callable

import libnacl.secret
from base58 import b58decode

def decode_err_handler(error):
    length = error.end - error.start
    return length * ' ', error.end


# copied from validator-info from plenum
codecs.register_error('decode_errors', decode_err_handler)


def compose_cmd(cmd):
    if os.name != 'nt':
        cmd = ' '.join(cmd)
    return cmd


def run_shell_command(command, timeout=300):
    try:
        ret = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, timeout=timeout)
        ret_bytes = ret.stdout
    except subprocess.CalledProcessError as ex:
        ret_bytes = ex.output
    except Exception as ex:
        raise Exception("command {} failed with {}".format(command, ex))
    ret_msg = ret_bytes.decode(locale.getpreferredencoding(), 'decode_errors').strip() if ret_bytes else ""
    return ret_msg


def parse_deps(deps: str):
    ret = []
    deps = deps.replace("|", ",")
    pkgs = deps.split(",")
    for pkg in pkgs:
        if not pkg:
            continue
        name_ver = pkg.strip(" ").split(" ", maxsplit=1)
        name = name_ver[0].strip(" \n")
        ver = None
        op = None
        if len(name_ver) == 2:
            ver_op = name_ver[1].strip("() \n").split(" ", maxsplit=1)
            op = ver_op[0]
            ver = ver_op[1]
        ret.append((name, ver, op))
    return ret


def get_info_from_package_manager(package):
    cmd = compose_cmd(['dpkg', '-s', package])
    return run_shell_command(cmd)


def parse_pkt_mgr_output(output):
    out_lines = output.split("\n")
    pkg_name = None
    ver = None
    deps = []
    lic = None
    for ln in out_lines:
        act_line = ln.strip(" \n").split(":", maxsplit=1)
        if act_line[0] == "Package":
            pkg_name = act_line[1].strip(" \n")
        if act_line[0] == "License":
            lic = act_line[1].strip(" \n")
        if act_line[0] == "Depends":
            deps = parse_deps(act_line[1].strip(" \n"))
        if act_line[0] == "Version":
            ver = act_line[1].strip(" \n")

    return pkg_name, ver, lic, deps


def build_info(pkg, sort_set = set(), lvl = -1):
    if lvl == 0:
        return []
    ret_list = []
    out_str = get_info_from_package_manager(pkg)
    pkg_name, ver, lic, deps = parse_pkt_mgr_output(out_str)
    if pkg_name in sort_set:
        return ret_list
    ret_list.append((pkg_name, ver, lic, deps))
    sort_set.add(pkg_name)
    nlvl = lvl - 1
    for d in deps:
        ret_list += build_info(d[0], sort_set, lvl=nlvl)
    return ret_list


def nte(val):
    if val is None:
        return ""
    return val


if __name__ == '__main__':
    pkg_name = sys.argv[1]
    res = build_info(pkg_name, lvl=4)
    for r in res:
        if not r or not r[0]:
            continue
        deps = ""
        for d in r[3]:
            if not d:
                continue
            deps += "{}{}{} ".format(d[0], nte(d[2]), nte(d[1]))
        print("{}\t{}\t{}\t{}".format(r[0], nte(r[1]), nte(r[2]), deps))
