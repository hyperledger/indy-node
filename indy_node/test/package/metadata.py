import pytest

from indy_node.__metadata__ import prepare_version


def test_prepare_version_default():
    prepare_version()


def test_prepare_version_wrong_data():
    for version in [
        '1',
        1,
        (1, 2, 3),
        (1, 2, 3, 4, 5),
        (1, 2, 3, 'alpha', 5),
        (1, 2, 3, 'dev', 5, 6)
    ]:
        with pytest.raises(AssertionError):
            prepare_version(version)


def test_prepare_version_stable():
    prepare_version((1, 2, 3, 'stable', 2)) == "1.2.3"


def test_prepare_version_dev():
    prepare_version((1, 2, 3, 'dev', 1)) == "1.2.3.dev1"


def test_prepare_version_rc():
    prepare_version((1, 2, 3, 'rc', 2)) == "1.2.3.rc2"
