Documenting XC exceptions
=========================

XC contains a Sphinx extension that will generate documentation for
your exceptions.

.. _Sphnx:

Enable the ``autoxc`` directive
-------------------------------

Add ``rjgtoys.xc.autodoc`` to the extensions listed in your `conf.py` Sphinx
configuration.  For example, add the following::

    extensions.extend([
        'rjgtoys.xc.autodoc'
    ])

This adds a new directive, ``autoxc``, that will generate documentation for
XC exceptions.

Example markup and output
-------------------------

The example web API server and client provided with the XC source code use
an exception called :class:`~examples.apierrors.OpError` to signal a problem with an operation:

.. literalinclude:: ../../examples/apierrors.py

To document that, include an ``autoxc`` directive in your Sphinx markup::

  .. autoxc:: examples.apierrors.OpError

The result is as follows:

.. autoxc:: examples.apierrors.OpError

Compare the plain ``autoexception`` output:

.. autoexception:: examples.apierrors.OpError

