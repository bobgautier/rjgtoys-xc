# XC: Structured exceptions for Python

XC encourages a structured, disciplined approach to use of exceptions: it reduces the
overhead of declaring exceptions that are specific to a cause,
and that contain information of use to the handler.   That in turn makes it easier
to write concise handlers.

A Sphinx extension makes it easy to produce good documentation from properly declared exceptions.

XC exceptions can be serialised into standard-compliant, language-independent JSON,
which makes them easy to use in web APIs, even when the consumer is not written in Python.

Read the documentation at http://rjgtoys.readthedocs.org/projects/xc/
