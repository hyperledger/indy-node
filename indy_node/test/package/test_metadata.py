import pytest
import json
import os

from indy_common.node_version import NodeVersion, InvalidVersionError
from plenum.__metadata__ import (
    set_version, load_version,
    set_manifest, load_manifest
)


def tmp_file_path(tdir, request, file_name):
    return os.path.join(
        tdir,
        "{}.{}".format(os.path.basename(request.node.nodeid), file_name)
    )


@pytest.fixture
def version_file_path(tdir, request):
    return tmp_file_path(tdir, request, '__version__.json')


@pytest.fixture
def manifest_file_path(tdir, request):
    return tmp_file_path(tdir, request, '__manifest__.json')


def idfn(v):
    return str(v).replace(' ', '')


@pytest.mark.parametrize(
    'version',
    [
        '1',
        2,
        # (1, 2), TODO uncomment once new release logic becomes completed
        (1, 2, 3, 4, 5),
        (1, 2, 3, 'alpha', 5),
        (1, 2, 3, 'dev', 5, 6)
    ],
    ids=idfn
)
def test_load_version_invalid(version, version_file_path):
    with open(version_file_path, 'w') as _f:
        json.dump(version, _f)
    with pytest.raises(InvalidVersionError):
        load_version(version_file_path)


# TODO ??? wider coverage

@pytest.mark.parametrize(
    'version',
    [
        'a1.2.3',
        '1.2.3a1',
        '1.2.3b2',
        '1.2.3.post1',
        '1!1.2.3',
        '1.2.3+1',
        '1',
        # '1.2', TODO uncomment once new release logic becomes completed
        '1.2.3.4',
        2
    ],
    ids=idfn
)
def test_set_version_invalid(version, version_file_path):
    with pytest.raises(InvalidVersionError):
        set_version(version, version_file_path)


@pytest.mark.parametrize(
    'version',
    [
        '1.2.3',
        '1.2.3.rc1',
        '1.2.3.dev2',
    ]
)
def test_set_load_version_valid(version, version_file_path):
    set_version(version, version_file_path)
    assert load_version(version_file_path) == NodeVersion(version)



def test_load_absent_manifest(manifest_file_path):
    assert load_manifest(manifest_file_path) is None


# TODO ??? wider coverage
@pytest.mark.parametrize(
    'manifest',
    [
        1,
        [1, 2],
        None,
        {'k1': 'v1', "2": 2},
    ],
    ids=idfn
)
def test_set_load_manifest_valid(manifest, manifest_file_path):
    set_manifest(manifest, manifest_file_path)
    assert load_manifest(manifest_file_path) == manifest
