import subprocess
import shutil
import codecs
import locale

from stp_core.common.log import getlogger
from indy_common.util import compose_cmd


# Package manager command output could contain some utf-8 symbols
# to handle such a case automatic stream parsing is prohibited,
# decode error handler is added, proper decoder is selected

# copied from validator-info from plenum
def decode_err_handler(error):
    length = error.end - error.start
    return length * ' ', error.end


# copied from validator-info from plenum
codecs.register_error('decode_errors', decode_err_handler)


logger = getlogger()
TIMEOUT = 300
MAX_DEPS_DEPTH = 6


class NodeControlUtil:
    # Method is used in case we are interested in command output
    # errors are ignored
    # only critical errors are logged to journalctl
    @classmethod
    def run_shell_command(cls, command, timeout=TIMEOUT):
        try:
            ret = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, timeout=timeout)
            ret_bytes = ret.stdout
        except subprocess.CalledProcessError as ex:
            ret_bytes = ex.output
        except Exception as ex:
            raise Exception("command {} failed with {}".format(command, ex))
        ret_msg = ret_bytes.decode(locale.getpreferredencoding(), 'decode_errors').strip() if ret_bytes else ""
        return ret_msg

    # Method is used in case we are NOT interested in command output
    # everything: command, errors, output etc are logged to journalctl
    @classmethod
    def run_shell_script(cls, command, timeout=TIMEOUT):
        subprocess.run(command, shell=True, timeout=timeout, check=True)

    @classmethod
    def _get_curr_info(cls, package):
        cmd = compose_cmd(['dpkg', '-s', package])
        return cls.run_shell_command(cmd)

    @classmethod
    def _parse_deps(cls, deps: str):
        ret = []
        deps = deps.replace("|", ",")
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

    @classmethod
    def _pkts_dedup(cls, deps):
        ret = []
        processed = set()
        for d in deps:
            name_ver = d.split("=", maxsplit=1)
            if name_ver[0] not in processed:
                ret.append(d)
            processed.add(name_ver[0])
        return ret

    @classmethod
    def _parse_version_deps_from_pkt_mgr_output(cls, output):
        out_lines = output.split("\n")
        ver = None
        ext_deps = []
        for ln in out_lines:
            act_line = ln.strip(" \n")
            if act_line.startswith("Version:"):
                ver = ver or act_line.split(":", maxsplit=1)[1].strip(" \n")
            if act_line.startswith("Depends:"):
                ext_deps += cls._parse_deps(act_line.split(":", maxsplit=1)[1].strip(" \n"))
        return ver, cls._pkts_dedup(ext_deps)

    @classmethod
    def curr_pkt_info(cls, pkg_name):
        package_info = cls._get_curr_info(pkg_name)
        return cls._parse_version_deps_from_pkt_mgr_output(package_info)

    @classmethod
    def _get_info_from_package_manager(cls, *package):
        cmd_arg = " ".join(list(package))
        cmd = compose_cmd(['apt-cache', 'show', cmd_arg])
        return cls.run_shell_command(cmd)

    @classmethod
    def update_package_cache(cls):
        cmd = compose_cmd(['apt', 'update'])
        cls.run_shell_script(cmd)

    @classmethod
    def get_deps_tree(cls, *package, depth=0):
        ret = list(set(package))
        if depth < MAX_DEPS_DEPTH:
            package_info = cls._get_info_from_package_manager(*ret)
            _, deps = cls._parse_version_deps_from_pkt_mgr_output(package_info)
            deps_deps = []
            deps = list(set(deps) - set(ret))
            deps_deps.append(cls.get_deps_tree(*deps, depth=depth + 1))

            ret.append(deps_deps)
        return ret

    @classmethod
    def get_deps_tree_filtered(cls, *package, filter_list=[], depth=0):
        ret = list(set(package))
        filter_list = [f for f in filter_list if not list(filter(lambda x: f in x, ret))]
        if depth < MAX_DEPS_DEPTH and filter_list:
            package_info = cls._get_info_from_package_manager(*ret)
            _, deps = cls._parse_version_deps_from_pkt_mgr_output(package_info)
            deps_deps = []
            deps = list(set(deps) - set(ret))
            deps_deps.append(cls.get_deps_tree_filtered(*deps, filter_list=filter_list, depth=depth + 1))

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
            ret = cls.run_shell_command(cmd)

            hlds = ret.strip().split("\n")
            return [h for h in hlds if h]
        else:
            logger.info('apt-mark not found. Assume holds is empty.')
            return []
