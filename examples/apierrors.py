"""
Exception declarations for the example API

"""

from rjgtoys.xc import Error, Title

class OpError(Error):
    """Raised when an operation fails."""

    title = "The operation failed"

    detail = "Op {op}(a={a},b={b}) failed: {error}"

    op: str = Title("The name of the operation that failed")
    a: float = Title("The first operand of the operation")
    b: float = Title("The second operand of the operation")

    error: str = Title("The error message")


