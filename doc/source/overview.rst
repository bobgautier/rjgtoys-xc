Overview
========

XC encourages a structured, disciplined approach to use of exceptions: it reduces the
overhead of declaring exceptions that are specific to a cause,
and that contain information of use to the handler.   That in turn makes it easier
to write concise handlers.

A Sphinx extension makes it easy to produce good documentation from properly declared exceptions.

XC exceptions can be serialised into standard-compliant, language-independent JSON,
which makes them easy to use in web APIs, even when the consumer is not written in Python.

What's the problem this package solves?
---------------------------------------

A good exception will be specific to its cause, and will carry information
back to the handler that allows that cause to be identified, if necessary.

But it can be tedious to declare separate exception classes for every kind
of situation that can occur, and that can lead to 'overloading' of exception
classes - using a single class for multiple kinds of error.

The most extreme case of this tendency involves the use of :class:`Exception` itself.

You may have seen (or even written) code that raises exceptions like this::

    def split_host_port(spec):
        try:
            (host, port) = spec.split(':')
            port = int(port)
            return (host, port)
        except ValueError:
            raise Exception(f"Invalid host port specification: {spec}")

When a 'general purpose' exception class is used, handling the exception becomes
difficult.

When the class doesn't identify the cause, the only way to distinguish between
different causes is to analyse the content of the exception.

Sometimes there is no alternative but to write code like this::

    try:
        (h, p) = split_host_port(data)
    except Exception as e:
        if 'Invalid host port' not in str(e):
            raise

        print("Please specify in the form host:port")

When non-specific exception classes are used, the handler too has to be non-specific,
or has to resort to strange tricks to distinguish the cause.

Another problem with non-specific exceptions is that they can't present detailed information
about the cause in an easily accessed way.

In the above example, suppose you wanted to know the spec that had caused the exception.   In this simple
example it's easy enough to get at (in `data`) but that may not be so straightforward in real code.

The exception should provide information about its own cause, but in this case the only way to do that
is to examine the string representation of the exception::

    try:
        (h, p) = split_host_port(data)
    except Exception as e:
        t = str(e)
        if 'Invalid host port' not in t:
            raise

        s = t.rsplit(' ')[-1]

        print(f"Invalid spec '{s}'.  Please specify in the form host:port")


What's a "structured" exception?
--------------------------------

The "structure" that XC provides has a number of aspects:

 - It is easy to declare sufficiently specific exceptions
 - The exceptions can carry relevant information
 - ...which makes handlers simpler to write
 - The exceptions are easily (automatically) documented


Structured examples
-------------------

The above examples can be rewritten like this.

There is no avoiding having to declare the exception, but the declaration is
more terse than it might have been if based directly on :class:`Exception`.   In particular
you don't have to write any constructors or any other methods for your new exception.

::

    from rjgtoys.xc import Error, Title

    class InvalidHostPort(Error):
        """Raised when an host:port specification is wrong."""

        spec: str = Title("The invalid host:port string")

        detail = "Invalid host port specification: {spec}"


The raiser is a little more terse because it doesn't have to
construct the 'message' string::

    def split_host_port(spec):
        try:
            (host, port) = spec.split(':')
            port = int(port)
            return (host, port)
        except ValueError:
            raise InvalidHostPort(spec=spec)


The handler is now very specific::

    try:
        (h, p) = split_host_port(data)
    except InvalidHostPort as e:
        print(f"Invalid spec '{e.spec}'.  Please specify in the form host:port")


In the handler, you now have a specific exception class to catch, and furthermore, it delivers the detail that
you need to handle it properly, as an attribute of the exception.


Structured exceptions and APIs
------------------------------

XC exceptions don't just simplify your Python; they are designed to work well over web APIs too.

Every XC exception can be serialised to JSON, or constructed from JSON, so that if an XC exception
is raised in a (web) service it is easy to pass that exception back to the client, where it can
be reconstructed and re-raised there.

The JSON representation follows RFC7807_, and is not Python-specific; web
APIs that are implemented in Python using XC should be usable from other languages without
undue difficulty.

The examples include a very simple web API server based on FastAPI_ and a client for that API.

What is is built on?
--------------------

XC makes use of Python type annotations, via Pydantic_, which implements type-checked data classes.

.. _Pydantic: https://pydantic-docs.helpmanual.io/

.. _RFC7807: https://tools.ietf.org/html/rfc7807


.. _FastAPI: https://fastapi.tiangolo.com/

Why the name?
-------------

I wanted a short name for this package, because it's likely to be referenced often.

The name XC is the shortest meaningful abbreviation I could think of for 'Exception'.

