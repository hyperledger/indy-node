# TODO it's a copy-paste of common.version:
# remove once plenum is merged to node
# !!! do not try to import from plenum since that code might be
# called (imported) in raw env from metadata routine where
# no plenum, no 'packaging' ...

from typing import Tuple, Iterable, Union
from abc import abstractmethod, ABCMeta
import re


class InvalidVersionError(ValueError):
    pass


class Comparable(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def cmp(cls, v1: 'Comparable', v2: 'Comparable') -> int:
        """ Compares two instances. """

    def __lt__(self, other: 'Comparable') -> bool:
        return self.cmp(self, other) < 0

    def __gt__(self, other: 'Comparable') -> bool:
        return self.cmp(self, other) > 0

    def __eq__(self, other: 'Comparable') -> bool:
        return self.cmp(self, other) == 0

    def __le__(self, other: 'Comparable') -> bool:
        return self.cmp(self, other) <= 0

    def __ge__(self, other: 'Comparable') -> bool:
        return self.cmp(self, other) >= 0

    def __ne__(self, other: 'Comparable') -> bool:
        return self.cmp(self, other) != 0


class VersionBase(Comparable):

    @classmethod
    def cmp(cls, v1: 'VersionBase', v2: 'VersionBase') -> int:
        """ Compares two instances. """
        # TODO types checking
        if v1._version > v2._version:
            return 1
        elif v1._version == v2._version:
            return 0
        else:
            return -1

    @property
    @abstractmethod
    def full(self) -> str:
        """ Full version string. """

    @property
    @abstractmethod
    def parts(self) -> Iterable:
        """ Full version as iterable. """

    @property
    @abstractmethod
    def release(self) -> str:
        """ Release part string. """

    @property
    @abstractmethod
    def release_parts(self) -> Iterable:
        """ Release part as iterable. """

    def __init__(self, version: str, allow_non_stripped: bool = False):
        if not isinstance(version, str):
            raise InvalidVersionError('version should be a string')
        if not allow_non_stripped and version != version.strip():
            raise InvalidVersionError(
                'version includes leading and/or trailing spaces'
            )
        self._version = self._parse(version)

    def _parse(self, version: str):
        return version

    def __hash__(self):
        return hash(self.full)

    def __str__(self):
        return self.full

    def __repr__(self):
        return "{}(version='{}')".format(self.__class__.__name__, self.full)


class SourceVersion(VersionBase):
    pass


class PackageVersion(VersionBase):
    @property
    @abstractmethod
    def upstream(self) -> SourceVersion:
        """ Upstream part of the package. """


class SemVerBase(VersionBase):
    @property
    def major(self) -> str:
        return self.release_parts[0]

    @property
    def minor(self) -> str:
        return self.release_parts[1]

    @property
    def patch(self) -> str:
        return self.release_parts[2]


class GenericVersion(VersionBase):

    # combines allowed characters from:
    # - PyPI: https://www.python.org/dev/peps/pep-0440
    # - SemVer: https://semver.org/
    re_generic = re.compile(r'[0-9a-zA-Z.\-+!]+')

    @property
    def full(self) -> str:
        return self._version

    @property
    def parts(self) -> Iterable:
        return (self.full,)

    @property
    def release(self) -> str:
        return self.full

    @property
    def release_parts(self) -> Iterable:
        return self.parts

    def _parse(self, version):
        if not self.re_generic.fullmatch(version):
            raise InvalidVersionError('only alphanumerics and [.-+!] are allowed')
        return version


class PEP440VersionFallback(Comparable):
    """ Mimics packaging.version.Version. """

    # covers only some cases
    re_pep440 = re.compile(r'([0-9]+)\.([0-9]+)\.([0-9]+)(?:\.?(dev|rc|a|b)\.?([0-9]+))?')

    @classmethod
    def cmp(cls, v1: 'PEP440VersionFallback',
            v2: 'PEP440VersionFallback') -> int:
        """ Compares two instances. """
        raise NotImplementedError("Please, install 'packaging' package")

    def __init__(self, version: str):
        match = self.re_pep440.fullmatch(version)
        if not match:
            raise InvalidVersionError(
                "version '{}' is invalid, expected N.N.N[[.]{{a|b|rc|dev}}[.]N]"
                .format(version)
            )
        self._version = tuple(
            [int(p) if idx in (0, 1, 2, 4) and p is not None else p for idx, p in enumerate(match.groups())]
        )

    @property
    def public(self):
        return self.base_version + (
            '' if self._version[3] is None else
            "{}{}{}"
            .format(
                '.' if self.dev else '', self._version[3], self._version[4]
            )
        )

    @property
    def base_version(self):
        return "{}.{}.{}".format(*self.release)

    @property
    def epoch(self):
        return 0

    @property
    def release(self):
        return self._version[:3]

    @property
    def local(self):
        return None

    @property
    def pre(self):
        if self.is_prerelease and not self.is_devrelease:
            return self._version[3:]

    @property
    def is_prerelease(self):
        return self._version[3] in ('a', 'b', 'rc', 'dev')

    @property
    def dev(self):
        return self._version[4] if self.is_devrelease else None

    @property
    def is_devrelease(self):
        return self._version[3] == 'dev'

    @property
    def post(self):
        return None

    @property
    def is_postrelease(self):
        return False


class PEP440BasedVersion(GenericVersion):

    def _parse(self, version: str):

        # TODO test that
        try:
            from packaging.version import (
                Version as PEP440Version,
                InvalidVersion as PEP440InvalidVersion
            )
        except ImportError:
            # seems we work in pour environment
            PEP440Version = PEP440VersionFallback
            PEP440InvalidVersion = InvalidVersionError

        try:
            return PEP440Version(version)
        except PEP440InvalidVersion as exc:
            # TODO is it the best string to pass
            raise InvalidVersionError(str(exc))
        # TODO create API wrappers for dev, pre and post from PEP440Version

    @property
    def public(self) -> str:
        return self._version.public

    @property
    def full(self) -> str:
        res = self._version.public
        if self._version.local:
            res += "+{}".format(self._version.local)
        return res

    @property
    def parts(self) -> Iterable:
        # TODO
        #   - API for add_parts
        add_parts = (None, None)
        if self._version.dev:
            add_parts = ('dev', self._version.dev)
        elif self._version.pre:
            add_parts = self._version.pre
        elif self._version.post:
            add_parts = ('dev', self._version.post)
        return (
            self._version.epoch,
            *self.release_parts,
            *add_parts,
            self._version.local
        )

    @property
    def release(self) -> str:
        return '.'.join(map(str, self.release_parts))

    @property
    def release_parts(self) -> Iterable:
        return self._version.release
