import pytest

from indy_node.__metadata__ import split_version_from_str, check_version


def test_split_version_from_str_only_int():
    assert split_version_from_str("1.2.3.4.5") == [1, 2, 3, 4, 5]


def test_split_version_from_str_with_str():
    assert split_version_from_str("1.2.3.rc.5") == [1, 2, 3, 'rc', 5]


def test_check_version_right_case():
    check_version(split_version_from_str("1.2.3.rc.5"))


def test_check_version_wrong_case():
    with pytest.raises(ValueError):
        check_version(split_version_from_str("1.2.3.4.5"))
