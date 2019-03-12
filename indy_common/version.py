from typing import Type

from common.version import (
    InvalidVersionError, PEP440BasedVersion, SemVerBase,
    DigitDotVersion, SourceVersion, PackageVersion,
    PlenumVersion
)

from indy_common.constants import APP_NAME


class SchemaVersion(DigitDotVersion):
    def __init__(self, version: str, **kwargs):
        super().__init__(version, parts_num=(2, 3), **kwargs)


class TopPkgDefVersion(DigitDotVersion, SourceVersion):
    def __init__(self, version: str, **kwargs):
        super().__init__(version, parts_num=(2, 3), **kwargs)


class NodeVersion(PlenumVersion):
    pass


def src_version_cls(pkg_name: str = APP_NAME) -> Type[SourceVersion]:
    # TODO implement dynamic class resolving depending on packge name and config
    return NodeVersion if pkg_name == APP_NAME else TopPkgDefVersion
