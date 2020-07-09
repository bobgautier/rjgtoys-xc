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


class _ExceptionField:
    """Allows a Pydantic model to have fields that hold an exception value."""

    @classmethod
    def __get_validators__(cls):
        yield cls._validate

    @classmethod
    def _validate(cls, v):
        assert isinstance(v, Exception)
        return v


class BadExceptionBug(Bug):
    """Raised when some function or method raises an exception
    that it has not declared itself capable of raising.

    :param raised: The exception that was raised (and which is
            not in the allowed set)
    """

    raised: _ExceptionField = Title("The disallowed exception")

    detail = "Disallowed exception raised: {raised}"


class BadExceptionsInTestBug(Bug):

    """Raised on an attempt to patch something to
        raise an exception that it is not allowed to raise

    Args:
        name: Name of the object being tested
        exceptions: The exceptions that may not be raised
            by this object
    """

    oneline = "Test case for {name} raises bad exception(s): {exclist}"

    def unpack(self):
        self.exclist = ", ".join(map(repr, self.exceptions))
