from typing import Type

from common.version import (
    DigitDotVersion, SourceVersion, PackageVersion
)

from indy_common.constants import APP_NAME
from indy_common.node_version import NodeVersion


NodeVersion = NodeVersion


class SchemaVersion(DigitDotVersion):
    def __init__(self, version: str, **kwargs):
        super().__init__(version, parts_num=(2, 3), **kwargs)


class TopPkgDefVersion(DigitDotVersion, SourceVersion):
    def __init__(self, version: str, **kwargs):
        super().__init__(version, parts_num=(2, 3), **kwargs)


def src_version_cls(pkg_name: str = APP_NAME) -> Type[SourceVersion]:
    # TODO implement dynamic class resolving depending on packge name and config
    return NodeVersion if pkg_name == APP_NAME else TopPkgDefVersion
