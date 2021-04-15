def splitup(msg, codeblocked=False):
    lines = msg.splitlines(keepends=True)

    if codeblocked:
        front = lines[0]
        back = lines[-1]
        lines = lines[1:-1]
    else:
        front = ''
        back = ''

    msgs = []
    count = 1900
    lastidx = 0
    for idx, line in enumerate(lines):
        if (count := count - len(line)) < 0:
            msg = front + ''.join(lines[lastidx:idx]) + back
            msgs.append(msg)
            count = 1900
            lastidx = idx

    return msgs


class cached_property:
    """Simplified cached property.

    Remove once 3.8 becomes more widely available.
    """
    def __init__(self, func):
        self.__doc__ = func.__doc__
        self.func = func

    def __get__(self, instance, _class):
        if instance is None:
            return self

        value = self.func(instance)
        instance.__dict__[self.func.__name__] = value

        return value
