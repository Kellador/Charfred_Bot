from collections import OrderedDict


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
