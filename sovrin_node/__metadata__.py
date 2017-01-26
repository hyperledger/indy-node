"""
sovrin-node package metadata
"""
__version_info__ = (0, 1)
__version__ = '{}.{}.{}'.format(*(__version_info__ if len(__version_info__)==3 else __version_info__+(0,)))
__author__ = "Sovrin Foundation."
__license__ = "Apache 2.0"

__all__ = ['__version_info__', '__version__', '__author__', '__license__']

__dependencies__ = {
    "sovrin_common": ">=0.0.4",
}
