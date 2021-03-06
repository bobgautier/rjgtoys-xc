Documenting exception raising behaviour
=======================================

In addition to documenting the individual exceptions in
an interface, it is also necessary to document which of
those exceptions may be raised by the methods and functions
in that interface.

Languages like Java and Ada have mechanisms for declaring
the exceptions that a method or function is allowed to raise,
and those languages enforce that interface constraint.

Python (currently) has no such mechanism, but XC offers
a partial stand-in, in the form of the ``@raises``
decorator.

.. decorator:: raises(exc1, [exc2, exc_list...])

This specifies a list of exceptions, or exception classes, that may
be raised by the callable to which the decorator is applied.

.. note::
   This decorator may be applied to any function or
   method, but not (yet) to a class.

Each of the parameters ``exc1``, ``exc2``, ``exc_list`` may be:

An exception class (with no subclasses)
   The callable is permitted to raise an instance of this class.

An exception class (that has subclasses)
   The callable is permitted to raise an instance of this class
   or any of its subclasses.

A list of either of the above
   A parameter that is a list is simply 'flattened'; each
   member of the list is interpreted according to these three
   rules.

The decorator performs two functions:

1. It adds documentation of the exception-raising behaviour
   of the callable to which it is applied;
2. It creates a run-time check that the declared exception-raising
   behaviour is followed.  If an exception is raised that is not
   included in the permitted set, that exception is replaced by a :exc:`BadExceptionBug` exception
   that wraps the original (bad) exception.

Example: Enforcement

The following code defines a function that is declared capable of
raising an exception, but which can in fact raise another:

.. literalinclude:: ../../examples/enforcement.py



Example: Documentation
----------------------

Here are some exception declarations::

    class Failed(xc.Error):
        """Raised when something fails."""

        what: str = xc.Title("What failed")

        detail = "Failed to {what}"


    class FooError(xc.Error):
        """Base class for Foo errors."""

        pass

    class PleaseWait(FooError):
        """Raised when an operation can't be done right now."""

        howlong: int = xc.Title("Minimum amount of time to wait")

        detail = "Please wait at least {howlong} seconds"

    class Other(Exception):
        """Raised for some other condition."""
        pass

    class Bad(Exception):
        pass


Now a function that may raise them::


    @raises(Failed, FooError, Other, Bad)
    def foo():
        """Does a foo on a bar.

        This is yet more documentation about foo.

        """

        pass


The markup to document that would be something like this::

  .. autofunction:: examples.raiser.foo

  .. autoexception:: examples.raiser.Failed
  .. autoexception:: examples.raiser.FooError
  .. autoexception:: examples.raiser.PleaseWait
  .. autoexception:: examples.raiser.Other
  .. autoexception:: examples.raiser.Bad

And the result:

.. autofunction:: examples.raiser.foo
.. autoexception:: examples.raiser.Failed
.. autoexception:: examples.raiser.FooError
.. autoexception:: examples.raiser.PleaseWait
.. autoexception:: examples.raiser.Other
.. autoexception:: examples.raiser.Bad

Notice how the exception names in the description of :func:`~examples.raiser.foo` are
linked to the full description of the exception.

