"""
Control imports for XC
"""

from ._xc import XC, Title

# The following are put here simply so that their fully qualified
# names do not include _xc

class Bug(XC):
    """
    This is the base class for exceptions that should never occur at runtime.

    They indicate a programming error that is not recoverable.
    """

    pass


class Error(XC):
    """
    This is the base class for exceptions that may be recoverable.

    Packages should create subclasses of this.
    """

    pass
