from typing import Type

from plenum.common.version import (
    InvalidVersionError, PEP440BasedVersion, SemVerBase,
    DigitDotVersion, SourceVersion, PackageVersion
)

from indy_common.constants import APP_NAME


class SchemaVersion(DigitDotVersion):
    def __init__(self, version: str, **kwargs):
        super().__init__(version, parts_num=(2, 3), **kwargs)


class TopPkgDefVersion(DigitDotVersion, SourceVersion):
    def __init__(self, version: str, **kwargs):
        super().__init__(version, parts_num=(2, 3), **kwargs)


class NodeVersion(
    PEP440BasedVersion, SemVerBase, SourceVersion, PackageVersion
):
    def __init__(self, version: str, **kwargs):
        super().__init__(version, **kwargs)

        # additional restrictions
        if self._version.pre:
            if self._version.pre[0] != 'rc':
                raise InvalidVersionError(
                    "pre-release phase '{}' is unexpected"
                    .format(self._version.pre[0])
                )

        if self._version.post:
            raise InvalidVersionError("post-release is unexpected")

        if self._version.epoch:
            raise InvalidVersionError("epoch is unexpected")

        if self._version.local:
            raise InvalidVersionError("local version part is unexpected")

        if len(self.release_parts) != 3:
            raise InvalidVersionError(
                "release part should contain only 3 parts")

    @property
    def upstream(self) -> SourceVersion:
        """ Upstream part of the package. """
        return self


def src_version_cls(pkg_name: str = APP_NAME) -> Type[SourceVersion]:
    # TODO implement dynamic class resolving depending on packge name and config
    return NodeVersion if pkg_name == APP_NAME else TopPkgDefVersion
