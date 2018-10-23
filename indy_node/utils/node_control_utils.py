import subprocess
import shutil

from stp_core.common.log import getlogger
from indy_common.util import compose_cmd

logger = getlogger()
TIMEOUT = 300
MAX_DEPS_DEPTH = 6


class NodeControlUtil:
    @classmethod
    def run_shell_command(cls, command, timeout):
        return subprocess.run(command, shell=True, check=True, universal_newlines=True,
                              stdout=subprocess.PIPE, timeout=timeout)

    @classmethod
    def run_shell_script(cls, command, timeout):
        return subprocess.run(command, shell=True, timeout=timeout)

    @classmethod
    def _get_curr_info(cls, package):
        cmd = compose_cmd(['dpkg', '-s', package])
        try:
            ret = cls.run_shell_command(cmd, TIMEOUT)
        except Exception as ex:
            return ""
        if ret.returncode != 0:
            return ""
        return ret.stdout.strip()

    @classmethod
    def _parse_version_deps_from_pkt_mgr_output(cls, output):
        def _parse_deps(deps: str):
            ret = []
            pkgs = deps.split(",")
            for pkg in pkgs:
                if not pkg:
                    continue
                name_ver = pkg.strip(" ").split(" ", maxsplit=1)
                name = name_ver[0].strip(" \n")
                if len(name_ver) == 1:
                    ret.append(name)
                else:
                    ver = name_ver[1].strip("()<>= \n")
                    ret.append("{}={}".format(name, ver))
            return ret

        out_lines = output.split("\n")
        ver = None
        ext_deps = []
        for ln in out_lines:
            act_line = ln.strip(" \n")
            if act_line.startswith("Version:"):
                ver = act_line.split(":", maxsplit=1)[1].strip(" \n")
            if act_line.startswith("Depends:"):
                ext_deps = _parse_deps(act_line.split(":", maxsplit=1)[1].strip(" \n"))
        return ver, ext_deps

    @classmethod
    def curr_pkt_info(cls, pkg_name):
        package_info = cls._get_curr_info(pkg_name)
        return cls._parse_version_deps_from_pkt_mgr_output(package_info)

    @classmethod
    def _get_info_from_package_manager(cls, package):
        cmd = compose_cmd(['apt-cache', 'show', package])
        try:
            ret = cls.run_shell_command(cmd, TIMEOUT)
        except Exception as ex:
            return ""
        if ret.returncode != 0:
            return ""
        return ret.stdout.strip()

    @classmethod
    def update_package_cache(cls):
        cmd = compose_cmd(['apt', 'update'])
        ret = cls.run_shell_command(cmd, TIMEOUT)
        if ret.returncode != 0:
            raise Exception('cannot update package cache since {} returned {}'.format(cmd, ret.returncode))
        return ret.stdout.strip()

    @classmethod
    def get_deps_tree(cls, package, depth=0):
        ret = [package]
        if depth < MAX_DEPS_DEPTH:
            package_info = cls._get_info_from_package_manager(package)
            _, deps = cls._parse_version_deps_from_pkt_mgr_output(package_info)
            deps_deps = []
            for dep in deps:
                deps_deps.append(cls.get_deps_tree(dep, depth=depth + 1))
            ret.append(deps)
            ret.append(deps_deps)
        return ret

    @classmethod
    def dep_tree_traverse(cls, dep_tree, deps_so_far):
        if isinstance(dep_tree, str) and dep_tree not in deps_so_far:
            deps_so_far.append(dep_tree)
        elif isinstance(dep_tree, list) and dep_tree:
            for d in reversed(dep_tree):
                cls.dep_tree_traverse(d, deps_so_far)

    @classmethod
    def get_sys_holds(cls):
        if shutil.which("apt-mark"):
            cmd = compose_cmd(['apt-mark', 'showhold'])
            try:
                ret = cls.run_shell_command(cmd, TIMEOUT)
            except Exception as ex:
                return []
            if ret.returncode != 0:
                return []

            hlds = ret.stdout.strip().split("\n")
            return [h for h in hlds if h]
        else:
            logger.info('apt-mark not found. Assume holds is empty.')
            return []
