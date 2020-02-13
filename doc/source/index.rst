rjgtoys.xc: Structured Exceptions for Python
============================================

XC encourages a structured, disciplined approach to use of exceptions: where they are
raised, it reduces the overhead of declaring exceptions that are specific to a cause,
and that contain information of use to the handler.   That in turn makes it easier
to write concise handlers.

XC exceptions are also easy to use in Web APIs: they serialise into (and deserialise from) language-independent
JSON, so they are easy to transport over a network.

.. toctree::
   :maxdepth: 2

   overview
   tutorial
   webapi
   autodoc
   raises
   getting
   todo




