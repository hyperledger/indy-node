import os


def module_path(module):
    return os.path.abspath(os.path.dirname(module.__file__))
