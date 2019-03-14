from typing import Iterable
import re


class InvalidVersionError(ValueError):
    pass


class NodeVersionFallback:
    """ Provide basic PEP440 based validation in raw python environment. """

    # covers only some cases
    re_pep440 = re.compile(r'([0-9]+)\.([0-9]+)\.([0-9]+)(?:\.?(dev|rc)\.?([0-9]+))?')

    def __init__(self, version: str):
        try:
            match = self.re_pep440.fullmatch(version)
        except TypeError as exc:
            raise InvalidVersionError(str(version)) from exc

        if not match:
            raise InvalidVersionError(
                "version '{}' is invalid, expected N.N.N[[.]{{dev|rc}}[.]N]"
                .format(version)
            )
        self._version = tuple(
            [int(p) if idx in (0, 1, 2, 4) and p is not None else p for idx, p in enumerate(match.groups())]
        )

    @property
    def public(self):
        return "{}.{}.{}".format(*self._version[:3]) + (
            '' if self._version[3] is None else
            "{}{}{}"
            .format(
                '.' if self._version[3] == 'dev' else '', *self._version[3:]
            )
        )

    @property
    def full(self) -> str:
        return self.public

    @property
    def parts(self) -> Iterable:
        add_parts = (None, None)
        if self._version[3] in ('rc', 'dev'):
            add_parts = self._version[3:]
        return (
            *self.release_parts,
            *add_parts,
        )

    @property
    def release(self) -> str:
        return '.'.join(map(str, self.release_parts))

    @property
    def release_parts(self) -> Iterable:
        return self._version[:3]

    @property
    def major(self) -> str:
        return self.release_parts[0]

    @property
    def minor(self) -> str:
        return self.release_parts[1]

    @property
    def patch(self) -> str:
        return self.release_parts[2]

    @property
    def upstream(self) -> 'NodeVersionFallback':
        """ Upstream part of the package. """
        return self

    def __str__(self):
        return self.full

    def __repr__(self):
        return "{}(version='{}')".format(self.__class__.__name__, self.full)

    def __hash__(self):
        return hash(self.full)

    def __eq__(self, other: 'NodeVersionFallback') -> bool:
        return self._version == other._version

    def __ne__(self, other: 'NodeVersionFallback') -> bool:
        return not (self == other)
