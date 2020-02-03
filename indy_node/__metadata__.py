"""
indy-node package metadata
"""
import os
import json
from typing import Any
import collections.abc

from indy_common.node_version import NodeVersion, InvalidVersionError

VERSION_FILENAME = '__version__.json'
VERSION_FILE = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), VERSION_FILENAME)


MANIFEST_FILENAME = '__manifest__.json'
MANIFEST_FILE = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), MANIFEST_FILENAME)


# TODO use/wrap plenum's set and load API
def load_version(version_file: str = VERSION_FILE) -> NodeVersion:
    with open(version_file, 'r') as _f:
        version = json.load(_f)
        if not isinstance(version, collections.abc.Iterable):
            raise InvalidVersionError(
                "Failed to load from {}: data '{}' is not iterable"
                .format(version_file, version)
            )
        return NodeVersion('.'.join([str(i) for i in version if str(i)]))


def set_version(version: str, version_file: str = VERSION_FILE):
    version = NodeVersion(version)
    with open(version_file, 'w') as _f:
        json.dump(['' if i is None else i for i in version.parts], _f)
        _f.write('\n')


def load_manifest(manifest_file: str = MANIFEST_FILE) -> Any:
    try:
        with open(manifest_file, 'r') as _f:
            return json.load(_f)
    except IOError:
        return None


def set_manifest(manifest: Any, manifest_file: str = MANIFEST_FILE):
    with open(manifest_file, 'w') as _f:
        json.dump(manifest, _f)
        _f.write('\n')


__title__ = 'indy-node'
__version_info__ = load_version()
__version__ = __version_info__.full
__manifest__ = load_manifest()
__description__ = 'Indy node'
__long_description__ = __description__
__keywords__ = 'Indy Node'
__url__ = 'https://github.com/hyperledger/indy-node'
__author__ = "Hyperledger"
__author_email__ = 'hyperledger-indy@lists.hyperledger.org'
__maintainer__ = "Hyperledger"
__license__ = "Apache 2.0"


__all__ = [
    '__title__', '__version_info__', '__version__', '__manifest__',
    '__description__', '__long_description__', '__keywords__',
    '__url__', '__author__', '__author_email__', '__maintainer__',
    '__license__', 'load_version', 'set_version', 'load_manifest', 'set_manifest']
