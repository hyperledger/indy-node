from indy_common.compat_set import CompatSet


def _order_test(old, diff, addition, expected):
    val = CompatSet(old).difference(diff)
    val.update(addition)
    assert list(val) == expected


def test_empty_set():
    val = CompatSet()
    assert len(val) == 0
    assert 99 not in val
    assert None not in val
    assert "" not in val
    assert "1" not in val

    assert val == CompatSet()
    assert val != CompatSet([1])
    assert val == set()
    assert val != {1}
    assert val != dict()


def test_simple_set():
    val = CompatSet([1, 2, 3])
    assert len(val) == 3

    assert 2 in val
    assert 99 not in val
    assert None not in val
    assert "" not in val
    assert "1" not in val

    assert val == CompatSet([2, 1, 3])
    assert val == {1, 2, 3}
    assert val != {1}
    assert val != set()
    assert val != dict()


def test_copy_simple():
    val = CompatSet([12, 4, 5, 6])
    assert list(val) == [5, 12, 4, 6]
    val = val.copy()
    assert list(val) == [5, 12, 4, 6]


def test_copy_removed():
    val = CompatSet([12, 4, 5, 6, 3])
    assert list(val) == [5, 3, 12, 4, 6]
    val.remove(5)
    assert list(val) == [3, 12, 4, 6]
    val = val.copy()
    assert list(val) == [3, 12, 4, 6]


def test_difference():
    val = CompatSet([1, 2])
    dif = val.difference([2, 3])
    assert val == CompatSet([1, 2])
    assert dif == CompatSet([1])

    assert 1 in dif
    assert 2 not in dif

    assert CompatSet([1, 2]) - {2, 3} == dif
    val -= {2, 3}
    assert val == dif
    assert CompatSet([1, 2]) - set() == {1, 2}
    assert CompatSet([1, 2]) - {1} == {2}


def test_intersection():
    val = CompatSet([1, 2])
    dif = val.intersection([2, 3])
    assert val == CompatSet([1, 2])
    assert dif == CompatSet([2])

    assert 2 in dif
    assert 1 not in dif

    assert CompatSet([1, 2]) & {2, 3} == dif
    val = CompatSet([1, 2])
    val &= {2, 3}
    assert val == dif


def test_isdisjoint():
    val = CompatSet([1, 2])
    assert val.isdisjoint(set())
    assert val.isdisjoint({3})
    assert not val.isdisjoint({2, 3})


def test_issubset():
    val = CompatSet([1, 2])
    assert val.issubset({1, 2, 3})
    assert val.issubset({1, 2})
    assert not val.issubset({1})
    assert not val.issubset(set())
    assert CompatSet().issubset({1})


def test_issuperset():
    val = CompatSet([1, 2])
    assert val.issuperset(set())
    assert val.issuperset({1})
    assert val.issuperset({1, 2})
    assert not val.issuperset({1, 2, 3})
    assert CompatSet().issuperset(set())
    assert not CompatSet().issuperset({1})


def test_symmetric_difference():
    val = CompatSet([1, 2])
    dif = val.symmetric_difference([2, 3])
    assert val == CompatSet([1, 2])
    assert dif == CompatSet([1, 3])

    assert 1 in dif
    assert 2 not in dif

    assert CompatSet([1, 2]) ^ {2, 3} == dif
    val ^= {2, 3}
    assert val == dif
    assert CompatSet([1, 2]) ^ set() == {1, 2}
    assert CompatSet([1, 2]) ^ {1} == {2}


def test_update():
    val = CompatSet([1, 2])
    assert 2 in val
    assert 3 not in val
    val.update([3, 4])
    assert 3 in val
    assert 2 in val
    assert 99 not in val

    assert CompatSet([1, 2]) | {3} == {1, 2, 3}
    val = CompatSet([1, 2])
    val |= {3}
    assert val == {1, 2, 3}


def test_update_order():
    val = CompatSet([1, 7, 6, 5])
    assert list(val) == [1, 5, 6, 7]
    val.update([9])
    assert list(val) == [1, 9, 5, 6, 7]
    val.update([8])
    assert list(val) == [1, 5, 6, 7, 8, 9]


def test_difference_order():
    val = CompatSet([5, 6, 8, 9, 10, 11, 12]).difference([])
    assert list(val) == [5, 6, 8, 9, 10, 11, 12]
    val.update([16])
    assert list(val) == [16, 5, 6, 8, 9, 10, 11, 12]

    val = CompatSet([5, 6, 8, 9, 10, 11, 12])
    assert list(val) == [5, 6, 8, 9, 10, 11, 12]
    val.update([16])
    assert list(val) == [5, 6, 8, 9, 10, 11, 12, 16]


def test_order_simple():
    _order_test([12, 4, 5, 6], [], [13], [5, 13, 12, 4, 6])


def test_order_large():
    _order_test(
        [
            5,
            6,
            8,
            9,
            10,
            11,
            12,
            13,
            16,
            17,
            18,
            19,
            161,
            162,
            164,
            165,
            166,
            167,
            41,
            169,
            170,
            171,
            173,
            174,
            175,
            176,
            441,
            178,
            179,
            180,
            181,
            182,
            183,
            440,
            184,
            185,
            186,
            436,
            437,
            438,
            190,
            63,
            64,
            192,
            194,
            67,
            70,
            199,
            201,
            202,
            206,
        ],
        [],
        [442],
        [
            5,
            6,
            8,
            9,
            10,
            11,
            12,
            13,
            16,
            17,
            18,
            19,
            161,
            162,
            164,
            165,
            166,
            167,
            41,
            169,
            170,
            171,
            173,
            174,
            175,
            176,
            442,
            178,
            179,
            180,
            181,
            182,
            183,
            440,
            441,
            184,
            185,
            186,
            436,
            437,
            438,
            190,
            63,
            64,
            192,
            194,
            67,
            70,
            199,
            201,
            202,
            206,
        ],
    )


def test_order_fill():
    _order_test(
        [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
            27,
            28,
            29,
        ],
        [],
        [
            83,
            38,
            101,
            103,
            56,
            61,
            70,
            73,
            53,
            39,
            77,
            92,
            82,
            64,
            48,
            78,
            51,
            68,
            96,
            102,
            37,
            84,
            35,
            58,
            59,
            91,
            90,
            85,
            31,
            36,
            72,
            104,
            60,
            43,
            74,
            44,
            98,
            87,
            34,
            100,
            63,
            95,
            52,
            99,
            80,
            54,
            45,
            40,
            30,
            75,
            81,
            41,
            86,
            89,
            55,
            42,
            71,
            57,
            32,
            47,
            76,
            69,
            33,
            46,
            79,
            94,
            66,
            93,
            50,
            88,
            67,
            97,
            49,
            65,
            62,
        ],
        [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
            27,
            28,
            29,
            30,
            31,
            32,
            33,
            34,
            35,
            36,
            37,
            38,
            39,
            40,
            41,
            42,
            43,
            44,
            45,
            46,
            47,
            48,
            49,
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            76,
            77,
            78,
            79,
            80,
            81,
            82,
            83,
            84,
            85,
            86,
            87,
            88,
            89,
            90,
            91,
            92,
            93,
            94,
            95,
            96,
            97,
            98,
            99,
            100,
            101,
            102,
            103,
            104,
        ],
    )
