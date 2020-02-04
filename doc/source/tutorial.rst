Tutorial
========

Background: Pydantic
--------------------

XC is built on Pydantic_, a package that builds on the Python type annotation
mechanism to implement type-checked data classes.


.. _Pydantic: https://pydantic-docs.helpmanual.io/


Exception base classes
----------------------

XC defines two base classes for new exceptions:

 - :class:`Error` is intended to be the base class for new
   exceptions (or intermediate base classes) that might be
   raised and handled at runtime.

   Subclasses of :class:`Error` are associated with conditions
   and events that are part of a component interface.

 - :class:`Bug` is intended to be the base class for exceptions
   that indicate programming errors.   They indicate
   conditions that cannot be recovered from except by changing
   some code somewhere.

For example, an exception that indicates a parameter was out of
range might be a :class:`Error` but an exception that indicates
an unrecognised parameter name (or field name) might be a :class:`Bug`.

Declaring an exception
----------------------

An XC exception is declared as a class in the usual way.

The base class is usually :class:`Error`.

An XC exception class will declare two kinds of attribute:

1. Class or `Metadata` attributes, which describe the exception class, and apply to all instances.  These attributes
can only be set when the class is declared.
2. Instance attributes, which are set on each instance, and must usually be specified in the constructor call,
although it is possible to set default values if that is appropriate.


Class or `metadata` attributes
******************************

The class or `metadata` attributes correspond to the attributes defined in RFC7807_ with some slight adjustments
to improve the fit to Python.   The descriptions below are based on those in RFC7807.

.. _RFC7807: https://tools.ietf.org/html/rfc7807

typename:\ str
  An identifier for the exception type   The default is the fully-qualified Python class name.
  This corresponds to the RFC7807 `type` attribute, but it is renamed in Python to avoid
  possible confusion.   The name `type` is however used in the JSON representation of
  XC exceptions, in accordance with RFC7807

title:\ str
  A short, human-readable summary of the problem type.   The default is the first line of the
  class docstring.

detail:\ str
  A ``format`` template that when evaluated will produce a human-readable message describing a
  specific instance of this exception.   The template will normally refer to instance attributes.
  This attribute is used when constructing the default string representation of the exception.

status:\ int
  The HTTP status code associated with this exception.   If the exception is used to generate a
  response to an HTTP API, this is the status code that should be used in the response.  The
  default is 400.

These attributes may be set in the class declaration.

They cannot be set per-instance, via the class constructor.


Exception instance attributes
*****************************

Additional attributes may be declared, which will be attributes of each instance of the class.

Each attribute becomes a parameter of the class constructor.

The full power of the Python type annotation system (:mod:`typing`), Pydantic :mod:`pydantic.model` and
:mod:`pydantic.field` declarations may be used.

In particular, the Pydantic :class:`pydantic.Field` constructor may be used to specify attribute defaults,
validators, and descriptive title.

Setting a title on an attribute can greatly improve the automatically generated documentation, both in Sphinx
and in Web APIs.   To simplify setting just the title, XC provides a :func:`XC.Title` function, which is simpler
to call than Pydantic's :func:`pydantic.Field`.

Example Exception Declaration
-----------------------------

Here is an example of an exception declaration::

    from rjgtoys.xc import Error, Title
    from pydantic import Field

    class InsufficientSpace(Error):
        """Raised when a filesystem has insufficient space.""

        detail = "Filesystem {path} has only {avail} bytes free, need {need}"

        path: str = Title("The filesystem mount point")
        avail: int = Field(..., "Number of bytes free on the filesystem")
        need:  int = Title("Number of bytes needed")

In the above example, both ``Field`` and ``Title`` have been used, just by way of demonstration.


Handling an Exception
---------------------

XC exceptions can be caught and handled just like any others, either by specific class or by superclass.

Both the class- and instance-attributes of an exception are available to the handler::

    try:
        copy_file_to_dest(src, dst):
    except InsufficientSpace as e:
        print(e)
        print("Please free at least %d bytes, or try a different filesystem" % (e.need-e.avail))


