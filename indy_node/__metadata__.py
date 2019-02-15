"""
indy-node package metadata
"""

__version_info__ = (1, 7, 0, 'dev', 0)


# TODO tests
def prepare_version(version=None):
    if not version:
        version = __version_info__

    assert type(version) in (tuple, list)
    assert len(version) == 5

    major, minor, patch, pre_release_suffix, revision = version
    assert pre_release_suffix in ('dev', 'rc', 'stable')

    release_part = "{}.{}.{}".format(major, minor, patch)

    if pre_release_suffix == 'stable':
        return release_part
    else:
        return "{}.{}{}".format(release_part, pre_release_suffix, revision)


__title__ = 'indy-node'
__version__ = prepare_version()
__description__ = 'Indy node'
__long_description__ = __description__
__keywords__ = 'Indy Node'
__url__ = 'https://github.com/hyperledger/indy-node'
__author__ = "Hyperledger"
__author_email__ = 'hyperledger-indy@lists.hyperledger.org'
__maintainer__ = "Hyperledger"
__license__ = "Apache 2.0"


__all__ = [
    '__title__', '__version_info__', '__version__',
    '__description__', '__long_description__', '__keywords__',
    '__url__', '__author__', '__author_email__', '__maintainer__',
    '__license__']
