import subprocess
import shutil
import codecs
import locale
import re
from typing import Iterable, Type, Tuple, List, Union


from stp_core.common.log import getlogger
from common.version import (
    InvalidVersionError, SourceVersion, PackageVersion, GenericVersion
)

from indy_common.version import NodeVersion, src_version_cls
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


class ShellError(subprocess.CalledProcessError):
    def __init__(self, *args, exc: subprocess.CalledProcessError = None, **kwargs):
        if exc:
            super().__init__(exc.returncode, exc.cmd, output=exc.output, stderr=exc.stderr)
        else:
            super().__init__(*args, **kwargs)

    @property
    def stdout_decoded(self):
        return (self.stdout.decode(locale.getpreferredencoding(), 'decode_errors')
                if self.stdout else "")

    @property
    def stderr_decoded(self):
        return (self.stdout.decode(locale.getpreferredencoding(), 'decode_errors')
                if self.stderr else "")


# TODO use some library instead of dpkg fpr version routine
class DebianVersion(PackageVersion):
    cache = {}  # seems not actually necessary
    # https://www.debian.org/doc/debian-policy/ch-controlfields.html#version
    re_version = re.compile(r'(?:([0-9]):)?([0-9][a-zA-Z0-9.+\-~]*)')

    @classmethod
    def _cmp(cls, v1, v2):
        if v1 == v2:
            return 0
        else:
            cmd = compose_cmd(['dpkg', '--compare-versions', v1, 'gt', v2])
            try:
                NodeControlUtil.run_shell_script_extended(cmd)
            except ShellError as exc:
                if exc.stderr:
                    raise
                else:
                    return -1
            else:
                return 1

    @classmethod
    def cmp(cls, v1, v2):
        key = (v1.full, v2.full)
        if key not in cls.cache:
            cls.cache[key] = cls._cmp(*key)
            cls.cache[key[::-1]] = cls.cache[key] * (-1)

        return cls.cache[key]

    @classmethod
    def clear_cache(cls):
        cls.cache.clear()

    def __init__(
        self,
        version: str,
        keep_tilde: bool = False,
        upstream_cls: Type[Union[SourceVersion, None]] = GenericVersion
    ):
        parsed = self._parse(version, keep_tilde, upstream_cls)
        if not parsed[1]:
            raise InvalidVersionError(
                "{} is not a valid debian version".format(version)
            )

        self._version = version
        self._epoch, self._upstream, self._revision = parsed

    def _parse(
            self,
            version: str,
            keep_tilde: bool,
            upstream_cls: Type[SourceVersion],
    ):
        epoch = None
        upstream = None
        revision = None

        match = re.fullmatch(self.re_version, version)
        if match:
            epoch = match.group(1)
            upstream = match.group(2)
            if upstream:
                if not keep_tilde:
                    upstream = upstream.replace('~', '.')
                # TODO improve regex instead
                parts = upstream.split('-')
                if len(parts) > 1:
                    upstream = '-'.join(parts[:-1])
                    revision = parts[-1]
        return (
            epoch,
            upstream_cls(upstream) if upstream else None,
            revision
        )

    @property
    def full(self) -> str:
        return self._version

    @property
    def parts(self) -> Iterable:
        return (self.epoch, self.upstream, self.revision)

    @property
    def release(self) -> str:
        return self.full

    @property
    def release_parts(self) -> Iterable:
        return self.parts

    @property
    def epoch(self):
        return self._epoch

    @property
    def upstream(self):
        return self._upstream

    @property
    def revision(self):
        return self._revision


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

    # TODO actually this should replace `run_shell_script` but it needs
    # deep testing and verification since it impacts upgrade routine a lot
    @classmethod
    def run_shell_script_extended(
            cls, command, stdout=False, stderr=False,
            timeout=TIMEOUT, check=True):
        try:
            res = subprocess.run(
                command, shell=True, timeout=timeout, check=check,
                stdout=None if stdout else subprocess.PIPE,
                stderr=None if stderr else subprocess.PIPE)
        except subprocess.CalledProcessError as exc:
            raise ShellError(exc=exc) from exc
        else:
            return res.stdout.decode(locale.getpreferredencoding(), 'decode_errors').strip() if res.stdout else ""

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
                # TODO generally wrong logic since it replaces any
                # fuzzy (>=, < etc.) constraints with equality
                ret.append("{}={}".format(name, ver))
        return ret

    @classmethod
    def _pkgs_dedup(cls, deps):
        ret = []
        processed = set()
        for d in deps:
            name_ver = d.split("=", maxsplit=1)
            if name_ver[0] not in processed:
                ret.append(d)
            processed.add(name_ver[0])
        return ret

    @classmethod
    def _parse_version_deps_from_pkg_mgr_output(
            cls,
            output: str,
            upstream_cls: Type[Union[SourceVersion, None]] = None
    ):
        out_lines = output.split("\n")
        ver = None
        ext_deps = []
        num_pkgs = 0
        for ln in out_lines:
            act_line = ln.strip(" \n")
            if act_line.startswith("Version:"):
                # this method might be used for the dependnecy tree resolving
                # when 'output' includes data for multiple packages,
                # version info here doesn't make any sense in such a case
                num_pkgs += 1
                ver = (None if num_pkgs > 1 else
                       act_line.split(":", maxsplit=1)[1].strip(" \n"))
            if act_line.startswith("Depends:"):
                ext_deps += cls._parse_deps(act_line.split(":", maxsplit=1)[1].strip(" \n"))

        if ver and upstream_cls:
            try:
                ver = DebianVersion(ver, upstream_cls=upstream_cls)
            except InvalidVersionError as exc:
                logger.warning(
                    "Failed to parse debian version {}: {}"
                    .format(ver, exc)
                )
                ver = None
                ext_deps = []
        else:
            ver = None

        return ver, cls._pkgs_dedup(ext_deps)

    @classmethod
    def curr_pkg_info(cls, pkg_name: str) -> Tuple[PackageVersion, List]:
        package_info = cls._get_curr_info(pkg_name)
        return cls._parse_version_deps_from_pkg_mgr_output(
            package_info, upstream_cls=src_version_cls(pkg_name))

    @classmethod
    def get_latest_pkg_version(
            cls,
            pkg_name: str,
            upstream: SourceVersion = None,
            update_cache: bool = True) -> PackageVersion:

        upstream_cls = src_version_cls(pkg_name)

        if upstream and not isinstance(upstream, upstream_cls):
            raise TypeError(
                "'upstream' should be instance of {}, got {}"
                .format(upstream_cls, type(upstream))
            )

        if update_cache:
            cls.update_package_cache()

        try:
            cmd = compose_cmd(
                ['apt-cache', 'show', pkg_name, '|', 'grep', '-E', "'^Version: '"]
            )
            output = cls.run_shell_script_extended(cmd).strip()
        except ShellError as exc:
            # will fail if either package not found or grep returns nothing
            # the latter is unexpected and treated as no-data as well
            logger.info(
                "no-data for package '{}' found".format(pkg_name)
            )
        else:
            if output:
                versions = []

                for v in output.split('\n'):
                    dv = DebianVersion(v.split()[1], upstream_cls=upstream_cls)
                    if not upstream or (dv.upstream == upstream):
                        versions.append(dv)

                try:
                    return sorted(versions)[-1]
                except ShellError:
                    logger.warning(
                        "version comparison failed unexpectedly for versions: {}"
                        .format(versions)
                    )

        return None

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
            _, deps = cls._parse_version_deps_from_pkg_mgr_output(package_info)
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
            _, deps = cls._parse_version_deps_from_pkg_mgr_output(package_info)
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

    @classmethod
    def hold_packages(cls, packages):
        if shutil.which("apt-mark"):
            packages_to_hold = ' '.join(packages)
            cmd = compose_cmd(['apt-mark', 'hold', packages_to_hold])
            cls.run_shell_script(cmd)
            logger.info('Successfully put {} packages on hold'.format(packages_to_hold))
        else:
            logger.info('Skipping packages holding')
