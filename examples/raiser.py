

from rjgtoys import xc

from rjgtoys.xc.raises import raises

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


@raises(Failed, FooError, Other, Bad, IOError)
def foo():
    """Does a foo on a bar.

    This is yet more documentation about foo.

    """

    pass

#print(foo.__doc__)

