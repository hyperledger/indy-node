import pytest

from common.version import InvalidVersionError

from indy_common.constants import APP_NAME
from indy_common.version import (
    SchemaVersion, TopPkgDefVersion, NodeVersion, src_version_cls
)


def test_schema_version():
    for version in ['', '1', '1.2.3.4', '1.2.a']:
        with pytest.raises(InvalidVersionError):
            SchemaVersion(version)
    SchemaVersion('1.2')
    SchemaVersion('1.2.3')


def test_top_package_default_version():
    for version in ['', '1', '1.2.3.4', '1.2.a']:
        with pytest.raises(InvalidVersionError):
            TopPkgDefVersion(version)
    TopPkgDefVersion('1.2')
    TopPkgDefVersion('1.2.3')


def test_src_version_cls():
    assert src_version_cls() == NodeVersion
    assert src_version_cls(APP_NAME) == NodeVersion
    assert src_version_cls('some_package') == TopPkgDefVersion
