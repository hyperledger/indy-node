import pytest
import typing

from indy_common.strict_types import strict_types, decClassMethods


@strict_types()
def takesStr(s: str) -> int:
    try:
        return int(s)
    except ValueError:
        pass


def testInvalidArgumentType():
    with pytest.raises(TypeError):
        takesStr(1)


def testInvalidReturnType():
    with pytest.raises(TypeError):
        assert takesStr('return None')


def testValidInputAndReturn():
    takesStr('1')


@decClassMethods(strict_types())
class TestClass:

    def takesStr(self, s: str) -> int:
        try:
            return int(s)
        except ValueError:
            pass

    def takesInt(self, i: int) -> str:
        try:
            if i != 457:
                return str(i)
        except ValueError:
            pass


@pytest.fixture(scope="module")
def t():
    return TestClass()


def testWholeClassInvalidArgumentType(t):
    with pytest.raises(TypeError):
        t.takesStr(1)
    with pytest.raises(TypeError):
        t.takesInt('1')


def testWholeClassInvalidReturnType(t):
    with pytest.raises(TypeError):
        assert t.takesStr('return None')
        assert t.takesInt(457)


def testWholeClassValidInputAndReturn(t):
    t.takesStr('1')
    t.takesInt(1)
