import pytest

from indy_common.message_fields import DebianVersionField

deb_validator = DebianVersionField()


def test_deb_valid_version():
    assert not deb_validator.validate('1.2.3')
    assert not deb_validator.validate('1.2.3~rc.1')
    assert not deb_validator.validate('1.2.3~2')


def test_deb_invalid_version():
    assert 'includes more than one tilde' in deb_validator.validate('1.2.3~4~5')
    assert 'should contain three parts' in deb_validator.validate('1.2.3.4~5')
    assert 'only digits' in deb_validator.validate('a.1.2')
    assert 'only digits' in deb_validator.validate('1.b.3')
    assert 'only digits' in deb_validator.validate('1.2.c')
    assert 'unexpected pre-release' in deb_validator.validate('1.2.3~alpha.1')
    assert 'revision part should be a digit' in deb_validator.validate('1.2.3~rc.e')
    assert 'revision part should be a digit' in deb_validator.validate('1.2.3~d')


def test_deb_invalid_number_of_comp():
    assert 'should contain three parts' in deb_validator.validate('1')
    assert 'should contain three parts' in deb_validator.validate('1.2')
    assert 'version consists of 6' in deb_validator.validate('1.2.3~rc.1.1')
