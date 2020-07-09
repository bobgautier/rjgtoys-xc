"""

.. autoclass:: Thing
.. autoclass:: ThingChain

"""

import collections


class Thing(dict):
    """
    A :class:`dict`-like thing that behaves like a JavaScript object;
    attribute access and item access are equivalent.  This makes writing
    code that operates on things read from JSON or YAML much simpler
    because there's no need to use lots of square brackets and string
    quotes.
    """

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __getitem__(self, name):
        """Get an item, allowing dots to separate path components."""

        try:
            return super(Thing, self).__getitem__(name)
        except KeyError:
            if '.' not in name:
                raise
            # Otherwise try harder...

        (prefix, tail) = name.split('.', 1)

        return self[prefix][tail]

    __getattr__ = __getitem__

    def merge(self, other):
        """A recursive 'update'.

        Any members that are themselves mappings or sets
        are also updated.
        """

        self.dict_merge(self, other)

    @classmethod
    def dict_merge(cls, dest, other):
        """Merge one dict-like object into another."""

        #        print("merge %s into %s" % (other, dest))

        for (k, v) in other.items():
            try:
                orig = dest[k]
            except KeyError:
                dest[k] = v
                continue

            # Maybe it's another Thing, or similar

            try:
                orig.merge(v)
                continue
            except AttributeError:
                pass

            # Maybe it's a dict or similar

            if isinstance(orig, dict):
                dict_merge(orig, v)
                continue

            # Can't do lists or sets yet

            # By default, other takes precedence

            dest[k] = v


class ThingChain(collections.ChainMap):
    """This is a version of :class:`collections.ChainMap` adapted
    for :class:`Thing` - it adds attribute-style access.

    This an abandoned experiment.  See test_thing.py for a test
    case that demonstrates why I abandoned it.

    """

    def __getitem__(self, name):

        try:
            return super(ThingChain, self).__getitem__(name)
        except KeyError:
            if '.' not in name:
                raise
            # Otherwise try harder...

        (prefix, tail) = name.split('.', 1)

        for m in self.maps:
            try:
                return m[prefix][tail]
            except KeyError:
                pass

        return self.__missing__(name)

    __getattr__ = __getitem__
