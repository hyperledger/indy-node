"""
A Set collection with Python 3.5-compatible ordering characteristics.

Adapted from cpython/Objects/setobject.c (written by Raymond D. Hettinger)
https://github.com/python/cpython/blob/v3.5.10/Objects/setobject.c
"""

from collections import namedtuple
from io import StringIO
from typing import AbstractSet, Any, Iterable, Optional, Tuple


class _Entry(namedtuple("_Entry", ("elem", "hash"))):
    @classmethod
    def from_elem(cls, elem) -> "_Entry":
        return super().__new__(cls, elem, hash(elem))


MIN_SIZE = 8
LINEAR_PROBES = 9
PERTURB_SHIFT = 5
REMOVED = _Entry(None, 0)


class CompatSet:
    """Compatibility set."""

    def __init__(self, elems: Iterable = None):
        """Initialize the set."""
        self._inner = _CompatSetInner()
        if elems is not None:
            self._inner.update(elems)

    def add(self, elem):
        """Add element elem to the set."""
        self._inner.add(elem)

    def capacity(self) -> int:
        """Get the current allocated capacity of the set."""
        return self._inner._mask + 1

    def discard(self, elem):
        """Remove element elem from the set if it is present."""
        self._inner.discard(elem)

    def remove(self, elem):
        """
        Remove element elem from the set.

        Raises KeyError if elem is not contained in the set.
        """
        if not self._inner.discard(elem):
            raise KeyError(elem)

    def pop(self) -> Any:
        """
        Remove and return an arbitrary element from the set.

        Raises KeyError if the set is empty.
        """
        return self._inner.pop()

    def clear(self):
        """Remove all elements from the set."""
        self._inner = _CompatSetInner()

    def copy(self) -> "CompatSet":
        """Return a shallow copy of the set."""
        return CompatSet._from_inner(self._inner.copy())

    def difference(self, *others) -> "CompatSet":
        """Return a new set with elements in only this set."""
        inner = None
        for other in others:
            if inner is None:
                inner = self._inner.difference(other)
            else:
                inner = inner.difference_update(other)
        if inner is None:
            inner = self._inner.copy()
        return CompatSet._from_inner(inner)

    def symmetric_difference(self, other: AbstractSet) -> "CompatSet":
        """Return a new set with elements in either set but not both."""
        inner = _CompatSetInner()
        inner.update(other)
        inner = inner.symmetric_difference_update(self)
        return CompatSet._from_inner(inner)

    def intersection(self, *others) -> "CompatSet":
        """Return a new set with elements common to the set and all others."""
        inner = None
        for other in others:
            if inner is None:
                inner = self._inner.intersection(other)
            else:
                inner = inner.intersection(other)
        if inner is None:
            inner = self._inner.copy()
        return CompatSet._from_inner(inner)

    def update(self, *others):
        """Update the set from one or more iterators."""
        for other in others:
            self._inner.update(other)

    def isdisjoint(self, other: AbstractSet) -> bool:
        """Determine if there is no intersection between two sets."""
        if len(self) > len(other):
            (other, self) = (self, other)
        return all(elem not in self for elem in other)

    def issubset(self, other: AbstractSet) -> bool:
        """Test whether every element in the set is in other."""
        return all((elem in other) for elem in self)

    def issuperset(self, other: AbstractSet) -> bool:
        """Test whether every element in other is in the set."""
        return all((elem in self) for elem in other)

    def union(self, *others) -> "CompatSet":
        """Return a new set with elements from the set and all others."""
        inner = self._inner.copy()
        for other in others:
            inner.update(other)
        return CompatSet._from_inner(inner)

    def __iter__(self) -> "_CompatSetIter":
        """Iterate over the set."""
        return _CompatSetIter(self._inner)

    def __bool__(self) -> bool:
        """Get the truthy value of the set."""
        return self._inner._used > 0

    def __eq__(self, other) -> bool:
        """Compare two sets."""
        if isinstance(other, CompatSet):
            return other._inner == self._inner
        if isinstance(other, set):
            return len(other) == len(self) and all((elem in other) for elem in self)
        return False

    def __len__(self) -> int:
        """Get the length of the set."""
        return self._inner._used

    def __contains__(self, elem) -> bool:
        """Determine if the set contains elem (elem in self)."""
        return self._inner.contains(elem)

    def __and__(self, other: Iterable) -> "CompatSet":
        """Return a new set with elements common to both."""
        return self.intersection(other)

    def __iand__(self, other: Iterable) -> "CompatSet":
        """Make this set an intersection with the other set."""
        self._inner = self._inner.intersection(other)
        return self

    def __or__(self, other: Iterable) -> "CompatSet":
        """Return a new set with elements in only this set."""
        return self.union(other)

    def __ior__(self, other: Iterable) -> "CompatSet":
        """Add elements from the other set."""
        self._inner.update(other)
        return self

    def __sub__(self, other: Iterable) -> "CompatSet":
        """Return a new set with elements in only this set."""
        return self.difference(other)

    def __isub__(self, other: Iterable) -> "CompatSet":
        """Remove elements from the other set."""
        self._inner = self._inner.difference_update(other)
        return self

    def __xor__(self, other: AbstractSet) -> "CompatSet":
        """Return a new set with elements in either set but not both."""
        return self.symmetric_difference(other)

    def __ixor__(self, other: AbstractSet) -> "CompatSet":
        """Update this set with the symmetric intersection."""
        self._inner = self._inner.symmetric_difference_update(other)
        return self

    def __repr__(self) -> str:
        """Get the set representation."""
        s = StringIO()
        s.write("{")
        fst = True
        for elem in self:
            if not fst:
                s.write(", ")
            fst = False
            s.write(repr(elem))
        s.write("}")
        return s.getvalue()

    @classmethod
    def _from_inner(cls, inner: "_CompatSetInner") -> "CompatSet":
        slf = cls.__new__(cls)
        slf._inner = inner
        return slf


class _CompatSetInner:
    def __init__(self):
        self._fill = 0
        self._mask = MIN_SIZE - 1
        self._search = 0
        self._table = [None] * MIN_SIZE
        self._used = 0

    def add(self, elem):
        self.add_entry(_Entry.from_elem(elem))

    def add_entry(self, entry: _Entry):
        if self.insert_entry(entry) and self._fill * 3 >= (self._mask + 1) * 2:
            self.grow()

    def contains(self, elem) -> bool:
        return self.contains_entry(_Entry.from_elem(elem))

    def copy(self) -> "_CompatSetInner":
        res = _CompatSetInner()
        res.merge(self)
        return res

    def contains_entry(self, entry: _Entry):
        index = self.look_entry(entry)
        found = self._table[index]
        return found is not None and found is not REMOVED

    def difference(self, other: Iterable) -> "_CompatSetInner":
        if isinstance(other, (CompatSet, set)) and (self._used >> 2) <= len(other):
            res = _CompatSetInner()
            pos = 0
            if isinstance(other, CompatSet):
                inner = other._inner
                while True:
                    (pos, entry) = self.next(pos)
                    if entry is None:
                        break
                    if not inner.contains_entry(entry):
                        res.add_entry(entry)
            else:
                while True:
                    (pos, entry) = self.next(pos)
                    if entry is None:
                        break
                    if entry.elem not in other:
                        res.add_entry(entry)
            return res

        # If len(self) much more than len(other), it's more efficient to
        # simply copy and then iterate other looking for common elements
        res = self.copy()
        return res.difference_update(other)

    def difference_update(self, other: Iterable) -> "_CompatSetInner":
        if isinstance(other, CompatSet) and other._inner is self:
            return _CompatSetInner()
        for elem in other:
            self.discard(elem)
        # If more than 1/5 are removed, then resize them away
        if (self._fill - self._used) * 5 >= self._mask:
            self.grow()
        return self

    def discard(self, elem) -> bool:
        return self.discard_entry(_Entry.from_elem(elem))

    def discard_entry(self, entry: _Entry) -> bool:
        index = self.look_entry(entry)
        found = self._table[index]
        if found is not None and found is not REMOVED:
            self._table[index] = REMOVED
            self._used -= 1
            return True
        return False

    def grow(self):
        if self._used > 50000:
            sz = self._used * 2
        else:
            sz = self._used * 4
        self.resize(sz)

    def insert_entry(self, entry: _Entry) -> bool:
        index = self.look_entry(entry)
        found = self._table[index]
        if found is None:
            self._table[index] = entry
            self._fill += 1
            self._used += 1
            return True
        elif found is REMOVED:
            self._table[index] = entry
            self._used += 1
            return True
        else:
            return False  # present

    def insert_entry_clean(self, entry: _Entry):
        """
        Insert an entry known to not be present.

        Must only be used in a table with no removed entries.
        """
        mask = self._mask
        table = self._table
        i = entry.hash & mask
        perturb = entry.hash
        found = None

        while True:
            if table[i] is None:
                found = i
                break

            if i + LINEAR_PROBES <= mask:
                for j in range(i + 1, i + LINEAR_PROBES + 1):
                    if table[j] is None:
                        found = j
                        break

            if found is not None:
                break

            perturb >>= PERTURB_SHIFT
            i = (i * 5 + 1 + perturb) & mask

        table[found] = entry
        self._fill += 1
        self._used += 1

    def intersection(self, other: Iterable) -> "_CompatSetInner":
        """Return a new inner set representing the intersection with another."""
        res = _CompatSetInner()
        if isinstance(other, CompatSet):
            if other._inner is self:
                res.update(self)
            else:
                inner = other._inner
                if inner._used > self._used:
                    (self, other) = (other, self)
                pos = 0
                while True:
                    (pos, entry) = inner.next(pos)
                    if entry is None:
                        break
                    if self.contains_entry(entry):
                        res.add_entry(entry)
        else:
            for elem in other:
                entry = _Entry.from_elem(elem)
                if self.contains_entry(entry):
                    res.add_entry(entry)
        return res

    def look_entry(self, entry: _Entry) -> int:
        """Find an element in the set, or find an empty entry."""
        # The set must have at least one empty entry for this to terminate
        assert self._fill <= self._mask

        free_idx = None
        mask = self._mask
        table = self._table
        i = entry.hash & mask
        perturb = entry.hash

        while True:
            if table[i] is None:
                return i if free_idx is None else i
            elif table[i] is REMOVED and free_idx is None:
                free_idx = i
            elif table[i] == entry:
                return i

            if i + LINEAR_PROBES <= mask:
                for j in range(i + 1, i + LINEAR_PROBES + 1):
                    if table[j] is None:
                        return j if free_idx is None else j
                    elif table[j] is REMOVED and free_idx is None:
                        free_idx = j
                    elif table[j] == entry:
                        return j

            perturb >>= PERTURB_SHIFT
            i = (i * 5 + 1 + perturb) & mask

    def merge(self, other: "_CompatSetInner"):
        if other is self or not other._used:
            return

        # Do one big resize at the start, rather than incrementally
        # resizing as we insert new keys.  Expect that there will be no
        # (or few) overlapping keys.
        if (self._fill + other._used) * 3 >= (self._mask + 1) * 2:
            self.resize((self._used + other._used) * 2)

        # If our table is empty, and both tables have the same size, and
        # there are no removed entries, then just copy the entries.
        if self._fill == 0 and self._mask == other._mask and other._fill == other._used:
            self._table = other._table.copy()
            self._fill = other._fill
            self._used = other._used
            return

        # If our table is empty, we can use insert_entry_clean()
        if self._fill == 0:
            for entry in other._table:
                if entry is not None and entry is not REMOVED:
                    self.insert_entry_clean(entry)
            return

        # We can't assure there are no duplicates, so do normal insertions
        for entry in other._table:
            if entry is not None and entry is not REMOVED:
                self.insert_entry(entry)

    def next(self, pos: int) -> Tuple[int, Optional[_Entry]]:
        while True:
            if pos > self._mask:
                return (pos, None)
            entry = self._table[pos]
            pos += 1
            if entry is not None and entry is not REMOVED:
                return (pos, entry)

    def pop(self):
        i = self._search & self._mask
        if not self._used:
            raise KeyError("pop from empty set")

        while True:
            entry = self._table[i]
            if entry is None or entry is REMOVED:
                i += 1
                if i > self._mask:
                    i = 0
            else:
                break

        self._table[i] = REMOVED
        self._used -= 1
        self._search = i + 1
        return entry.elem

    def resize(self, min_used: int):
        """Adjust the allocated size of the set."""
        old_table = self._table
        assert min_used >= 0

        new_size = MIN_SIZE
        while new_size <= min_used:
            new_size *= 2

        self._table = [None] * new_size
        self._fill = 0
        self._mask = new_size - 1
        self._used = 0

        for entry in old_table:
            if entry is not None and entry is not REMOVED:
                self.insert_entry_clean(entry)

    def symmetric_difference_update(self, other: Iterable) -> "_CompatSetInner":
        if isinstance(other, CompatSet) and other._inner is self:
            return _CompatSetInner()
        for elem in other:
            entry = _Entry.from_elem(elem)
            if not self.discard_entry(entry):
                self.add_entry(entry)
        return self

    def update(self, other: Iterable):
        """Update the set from an iterator of elements."""
        if isinstance(other, CompatSet):
            self.merge(other._inner)
            return
        for elem in other:
            self.add(elem)

    def __eq__(self, other) -> bool:
        if isinstance(other, _CompatSetInner):
            if other._used != self._used:
                return False
            for pos in range(self._used):
                entry = self._table[pos]
                if (
                    entry is not None
                    and entry is not REMOVED
                    and not other.contains_entry(entry)
                ):
                    return False
            return True
        return False


class _CompatSetIter:
    def __init__(self, s: _CompatSetInner):
        self._s = s
        self._pos = 0

    def __iter__(self):
        return self

    def __next__(self):
        (self._pos, entry) = self._s.next(self._pos)
        if entry is None:
            raise StopIteration
        return entry.elem
