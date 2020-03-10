import time
from collections import OrderedDict, MutableMapping


class SimpleTTLDict(OrderedDict):
    """Super simple implementation of an OrderedDict with expiring
    items.

    Only deletes items that have outlived their ttl when new items
    are inserted.
    """
    def __init__(self, ttl_seconds=360):
        assert ttl_seconds >= 0

        super().__init__(self)
        self.ttl = ttl_seconds

    def _expire(self):
        """Deletes all dict items that have outlived their ttl."""
        now = int(time.time())
        while self:
            (key, (value, date)) = super().popitem(last=False)
            if now - date > self.ttl:
                continue
            else:
                super().__setitem__(key, (value, date))
                super().move_to_end(key, last=False)
                break

    def __setitem__(self, key, value):
        """Set d[key] to (value, date), where date is its creation time.

        Also removes all expired entries.
        """
        self._expire()
        super().__setitem__(key, (value, int(time.time())))
        super().move_to_end(key)

    def getvalue(self, key):
        """Gets the value from a (value, date) tuple of a given key."""
        return super().__getitem__(key)[0]

    def find(self, predicate):
        """Finds and returns the first value that satisifies a given
        predicate."""
        for (value, _) in reversed(self.values()):
            if predicate(value):
                return value


class SizedDict(OrderedDict):
    """Super simple implementation of an OrderedDict with a fixed size.

    Adding a new item after maximum size has been reached removes
    the oldest item to make room.
    """

    def __init__(self, max_size=100):
        assert max_size >= 1

        super().__init__(self)
        self.max_size = max_size

    def __setitem__(self, key, value):
        """Sets item and moves it to the end (in case of updates)"""
        super().__setitem__(key, value)
        super().move_to_end(key)
        self._prune()

    def _prune(self):
        """Prune any items out of max_size range."""
        while len(self) > self.max_size:
            self.popitem(last=False)

    def find(self, predicate):
        """Finds and returns the first value that satisifies a given
        predicate, LIFO style."""

        for value in reversed(self.values()):
            if predicate(value):
                return value
        else:
            return None


class InvertableMapping(MutableMapping):
    """MutableMapping which generates and updates
    an inverted read only version of its store.

    Special handling for mappings with values that are
    lists, in which case the first element will be
    swapped with the key.
    """

    def __init__(self, initial):
        self.store = initial
        self._inverted = {}

    @property
    def inverted(self):
        if self._inverted:
            return self._inverted
        else:
            try:
                self._invert()
            except AttributeError:
                pass  # Too early, Config hasn't loaded yet.
            finally:
                return self._inverted

    def _invert(self):
        self._inverted = {}
        for k, v in self.store.items():
            if isinstance(v, list):
                self._inverted.setdefault(v[0], []).append([k] + v[1:])
            else:
                self._inverted.setdefault(v, []).append(k)

    def __getitem__(self, key):
        return self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __setitem__(self, key, value):
        self.store[key] = value
        self._invert()

    def __delitem__(self, key):
        del self.store[key]
        self._invert()
