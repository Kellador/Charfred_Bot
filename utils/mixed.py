import re

formatpat = re.compile('^[`]{3}(?P<format>\w+|\s)')


def splitup(msg, codeblocked=False):
    msg = msg.splitlines(keepends=True)
    if codeblocked:
        s = formatpat.search(msg[0])
        if s.group('format'):
            front = f'```{s.group("format")}\n'
        back = '\n```'
    else:
        front = ''
        back = ''
    msg.reverse()
    msgs = []
    part = front
    while True:
        if len(msg) > 0:
            next = msg.pop()
        else:
            if part:
                part += back
                msgs.append(part)
            break

        if (len(part) + len(next)) < 1990:
            part += next
        else:
            part += back
            msgs.append(part)
            part = front + next

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
