Documenting XC exceptions
=========================

XC contains a Sphinx_ extension called ``rjgtoys.xc.autodoc`` that will generate
documentation for your XC exceptions.

.. _Sphinx: https://www.sphinx-doc.org/en/master/

This extension builds on the ``sphinx.ext.autodoc`` extension, and extends the ``autoexception`` directive so that it generates more detailed documentation for XC exceptions than for others.

Installation
------------

``rjgtoys.xc.autodoc`` depends on the ``sphinx_autodoc_typehints`` extension, which must be installed in order
for for it to work::

    pip install sphinx-autodoc-typehints

.. _sphinx_autodoc_typehints: https://github.com/agronholm/sphinx-autodoc-typehints

Enable the ``rjgtoys.xc.autodoc`` extension
-------------------------------------------

Add ``rjgtoys.xc.autodoc`` to the extensions listed in your `conf.py` Sphinx
configuration.  For example, add the following::

    extensions.extend([
        'rjgtoys.xc.autodoc'
    ])

There is no need to list either ``sphinx.ext.autodoc`` or ``sphinx_autodoc_typehints``; both are required, and will be
enabled automatically by ``rjgtoys.xc.autodoc``.

Example markup and output
-------------------------

The example module ``examples/insuffspace.py`` (included in the XC source code)
declares the following exception::

    class InsufficientSpace(Error):
        """Raised when a filesystem has insufficient space."""

        detail = "Filesystem {path} has only {avail} bytes free, need {need}"

        path: str = Title("The filesystem mount point")
        avail: int = Field(..., title="Number of bytes free on the filesystem")
        need:  int = Title("Number of bytes needed")

To document that, include an ``autoexception`` directive in your Sphinx markup::

  .. autoexception:: examples.insuffspace.InsufficientSpace

The result is as follows:

.. autoexception:: examples.insuffspace.InsufficientSpace

Compare the plain ``autoexception`` output:

.. The following directive is defined by rjgtoys.xc.autodoc
   purely for this purpose: it gives access to the plain
   autoexception behaviour, to allow a demonstration of
   the default treatment of an XC exception.

.. autoxc_as_exception:: examples.insuffspace.InsufficientSpace
