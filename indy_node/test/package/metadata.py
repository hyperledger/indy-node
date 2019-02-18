import pytest

from indy_node.__metadata__ import (
    check_version, set_version, load_version, pep440_version
)


# TODO ??? other type of cases
def test_check_version_fail():
    for version in [
        '1',
        1,
        (1, 2, 3),
        (1, 2, 3, 4, 5),
        (1, 2, 3, 'alpha', 5),
        (1, 2, 3, 'dev', 5, 6)
    ]:
        with pytest.raises(ValueError):
            check_version(version)


# TODO ??? other type of cases
def test_check_version_pass():
    for version in [
            (1, 2, 3, 'dev', 5),
            (1, 2, 3, 'rc', 5),
            (1, 2, 3, 'stable', 5)
    ]:
        check_version(version)


# TODO ??? other type of cases
def test_set_and_load_version(tmpdir):
    version_file = str(tmpdir.join("version.txt"))
    for version in [
        (1, 2, 3, 'dev', 5),
        (1, 2, 3, 'rc', 5),
        (1, 2, 3, 'stable', 5)
    ]:
        set_version(version, version_file)
        assert load_version(version_file) == list(version)


def test_pep440_version_default():
    pep440_version()


def test_pep440_version_stable():
    pep440_version((1, 2, 3, 'stable', 2)) == "1.2.3"


def test_pep440_version_dev():
    pep440_version((1, 2, 3, 'dev', 1)) == "1.2.3.dev1"


def test_pep440_version_rc():
    pep440_version((1, 2, 3, 'rc', 2)) == "1.2.3.rc2"
