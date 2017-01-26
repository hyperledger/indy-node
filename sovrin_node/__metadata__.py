"""
sovrin-node package metadata
"""
__version_info__ = (0, 1)
__version__ = '.'.join(map(str, __version_info__))
__author__ = "Sovrin Foundation."
__license__ = "Apache 2.0"

__all__ = ['__version_info__', '__version__', '__author__', '__license__']

__dependencies__ = {
    "sovrin_common": ">=0.0.4",
}
