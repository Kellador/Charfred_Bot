import time
from collections import OrderedDict


class SimpleTTLDict(OrderedDict):
    """Super simple implementation of an OrderedDict with expiring
    items.


    """
    def __init__(self, ttl_seconds=180):
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
