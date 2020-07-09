"""
Exceptions, particularly those that can be transported
over an HTTP REST API.

.. autoclass:: _XCContentModel
   :members:

.. autoexception:: XC
   :members: to_json, from_json

.. autoclass:: _XCContentModel

.. autoexception:: _XCBase

.. autoclass:: _XCType


"""

import urllib
import json

from pydantic import BaseModel, Field

from rjgtoys.xc._json import json_loads, json_dumps


def Title(t):
    """Simplifies model declarations a little."""

    return Field(..., title=t)


class _XCContentModel(BaseModel):
    """
    This is the base class for exception content - the values
    of parameters passed to their constructors.

    It's essentially :class:`pydantic.BaseModel`.
    """

    pass


"""
The Exception base class and the BaseModel don't
play nicely together; make Exceptions that carry
a BaseModel instance around, so that the two interfaces
can be kept separate.

"""


class _XCBase(Exception):
    """A hidden base class for exceptions."""

    _model = _XCContentModel

    def __init__(self, **kwargs):
        super(_XCBase, self).__init__()

        self._content = self._model.parse_obj(kwargs)

    def __getattr__(self, name):
        return getattr(self._content, name)

    @classmethod
    def parse_json(cls, data):
        return cls(**json_loads(data))

    def __eq__(self, other):
        """Two exceptions are identical if they are the same class and have the same content."""

        return (self.__class__ is other.__class__) and (self._content == other._content)


class _XCType(type):
    """Metaclass for exceptions."""

    def __new__(cls, name, bases, attrs):
        """Generate a new BaseException subclass.

        The attrs passed in are reorganised so that
        most are moved to an internal '_model' class
        that is derived from BaseModel (from the
        _model classes of the bases, in fact).
        """

        # Should this 'fully qualify'?

        qualname = '.'.join((attrs['__module__'], name))
        attrs.setdefault('typename', qualname)
        # Does this 'inherit' correctly?
        if 'title' not in attrs:
            title = attrs.get('__doc__', '\n').splitlines()[0]
            attrs['title'] = title

        exc_attrs = {}
        model_attrs = {}

        exc_attr_forced = ('typename', 'title', 'detail', 'status')

        for (n, v) in attrs.items():

            # Some go only to the exception class

            if n in exc_attr_forced:
                exc_attrs[n] = v
                continue

            if n.startswith('_'):
                exc_attrs[n] = v
                continue

            # Content items can't be callable

            if callable(v) or isinstance(v, (classmethod, staticmethod)):
                exc_attrs[n] = v
                continue

            # Otherwise, move it to model

            model_attrs[n] = v

        # UGLY: fix up the annotations of the model and the exception

        anns = attrs.get('__annotations__', {})

        # Capture annotations of any attributes that were put into the exception
        exc_ann = {k: anns[k] for k in exc_attrs if k in anns}
        # and anyway copy those for the forced attributes
        exc_ann.update({k: anns[k] for k in exc_attr_forced if k in anns})

        exc_attrs['__annotations__'] = exc_ann

        # Move all the rest to the model

        model_ann = {k: v for (k, v) in anns.items() if k not in exc_ann}

        model_attrs['__annotations__'] = model_ann

        #        print("Build %s exception %s from %s" % (cls.__name__, name, attrs))
        #        print("  Exception attrs %s" % (exc_attrs,))
        #        print("  Model attrs %s" % (model_attrs,))

        exc_doc = exc_attrs.get('__doc__', exc_attrs['title'])

        model_attrs['__doc__'] = exc_doc

        # Build the content model class

        model = type('_model', tuple(s._model for s in bases), model_attrs)

        exc_attrs['_model'] = model

        return type.__new__(cls, name, bases, exc_attrs)


class XC(_XCBase, metaclass=_XCType):
    """The base class for 'structured' exceptions.

    Provides a bit of structure on top of the language-provided
    :class:`Exception`.

    Each (sub-)class defines a set of parameters that are become
    attributes of the exception, available to handlers.

    Those parameters are type-checked and may have associated
    defaults and descriptions that are available to generate
    documentation and other forms of help.

    In particular, :class:`XC` subclasses can be serialised
    and deserialised as described in RFC7807, which makes
    them easy to use for building REST APIs.

    Each subclass should define the following attributes:

    typename
      The 'problem identifier' - defaults to the name of the class.

      This is used to generate the RFC7807 `type` attribute.

      If no value is set explicitly, the fully qualified name of the class is used.
    title
      A short human-readable description of the problem type.

      This is used as the RFC7807 `title` attribute.
    detail
      A format template that can produce a human-readable explanation
      specific to a particular instance of this exception.

      This is used to define the string representation of the exception (the `__str__` method)
      and also (via :func:`str`) to generate the RFC7807 `detail` attribute.
    status
      An HTTP status code associated with this exception.  Defaults to 400.

      This is used when the exception is transported over HTTP.

    The above attributes are defined in RFC 7807.

    """

    # The following are magically kept in the exception class, not the content

    typename: str
    title: str

    detail: str

    status: int = 400

    def __str__(self):
        try:
            return self.detail.format(**self._content.dict())
        except Exception as e:
            return "%s.__str__() -> %s" % (self.__class__.__name__, e)

    def to_dict(self):
        """Produce a JSON-encodable dict representing this exception.

        Returns an RFC7807-compliant JSON object.
        """

        content = self._content.dict()
        data = dict(
            type=self.typename,
            title=self.title,
            status=self.status,
            detail=str(self),
            instance="%s?%s" % (self.typename, urllib.parse.urlencode(content)),
            content=content,
        )
        return data

    @classmethod
    def from_obj(cls, data):
        """Reconstruct an exception from some data.

        Expects an object such as might be produced by
        parsing the result of calling :meth:`to_json()` on
        an instance of this class or a subclass of it.

        Returns an instance of the appropriate class, or
        raises :exc:`TypeError` if no class can be identified.
        """

        typename = data['type']

        for kls in all_subclasses(cls):
            if kls.typename == typename:
                return kls(**data['content'])

        raise TypeError("No %s type %s" % (cls.__name__, typename))

    @classmethod
    def from_json(cls, data):
        return cls.from_obj(json_loads(data))


def all_subclasses(cls):
    # pylint: disable=line-too-long
    # the following comment is simply too wide
    """Generate all subclasses of class `cls`.

    See: https://stackoverflow.com/questions/3862310/how-to-find-all-the-subclasses-of-a-class-given-its-name
    """

    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)]
    )
