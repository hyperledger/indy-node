#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

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


def testInvalidArgumentType():
    with pytest.raises(TypeError):
        takesStr(1)


def testInvalidReturnType():
    with pytest.raises(TypeError):
        assert takesStr('return None')


def testValidInputAndReturn():
    takesStr('1')


def testWorksWithComplexTypes():
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
