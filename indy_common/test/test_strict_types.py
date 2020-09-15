import pytest
import typing

from indy_common.strict_types import strict_types, decClassMethods


@strict_types()
def takesStr(s: str) -> int:
    try:
        return int(s)
    except ValueError:
        pass


@strict_types()
def takesUnion(s: typing.Union[str, None]) -> int:
    try:
        return int(s)
    except ValueError:
        pass


@pytest.mark.test
def test_invalid_argument_type():
    with pytest.raises(TypeError):
        takesStr(1)


@pytest.mark.test
def test_invalid_return_type():
    with pytest.raises(TypeError):
        assert takesStr('return None')


@pytest.mark.test
def test_valid_input_and_return():
    takesStr('1')


@pytest.mark.test
def test_works_with_complex_types():
    takesUnion('1')


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


@pytest.mark.test
def test_whole_class_invalid_argument_type(t):
    with pytest.raises(TypeError):
        t.takesStr(1)
    with pytest.raises(TypeError):
        t.takesInt('1')


@pytest.mark.test
def test_whole_class_invalid_return_type(t):
    with pytest.raises(TypeError):
        assert t.takesStr('return None')
        assert t.takesInt(457)


@pytest.mark.test
def test_whole_class_valid_input_and_return(t):
    t.takesStr('1')
    t.takesInt(1)
