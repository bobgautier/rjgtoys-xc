
from rjgtoys.xc import Bug

from rjgtoys.xc.raises import raises

class Allowed(Exception):
    """This exception may be raised by do_operation."""

    def __str__(self):
        return "I am allowed"

class NotAllowed(Exception):
    """This exception may not be raised by do_operation."""

    def __str__(self):
        return "I am not allowed"


@raises(Allowed)
def do_operation(ok: bool):
    if ok:
        raise Allowed()
    else:
        raise NotAllowed()

try:
    do_operation(True)
    assert False, "Should not be reached"
except Allowed:
    print("Expected exception raised")

try:
    do_operation(False)
    assert False, "Should not be reached"
except Bug:
    print("There is a bug in do_operation")
