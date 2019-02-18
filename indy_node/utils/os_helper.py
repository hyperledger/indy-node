import os


def module_path(module__file__):
    return os.path.abspath(os.path.dirname(module__file__))
