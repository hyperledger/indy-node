"""
sovrin-node package metadata
"""
__version_info__ = (0, 2)
__version__ = '.'.join(map(str, __version_info__))
__author__ = "Sovrin Foundation."
__license__ = "Apache 2.0"

__all__ = ['__version_info__', '__version__', '__author__', '__license__']

# TODO: Shouldn't we update these dependencies?
__dependencies__ = {
    "sovrin_common": ">=0.0.4",
}
