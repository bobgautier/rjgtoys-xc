"""
Test the constraint mechanisms in rjgtoys.xc.raises
"""

from rjgtoys.xc.raises import raises, may_raise, raises_exception

from rjgtoys.xc import BadExceptionBug, BadExceptionsInTestBug

import pytest
from unittest.mock import patch

# Fixtures

class Allowed1(Exception):
    """First allowed exception."""

    pass


class Allowed2(Exception):
    """Second allowed exception."""

    pass


def raise_a1():
    raise Allowed1()


def test_default_may_raise():
    """The raise_a1() function has the correct constraint and works correctly."""

    # Constraint was not given, so it can do anything

    assert may_raise(raise_a1) == set((Exception,))

    # It always raises the exception.

    with pytest.raises(Allowed1):
        raise_a1()

@raises(Allowed2)
def raise_a2(x):
    """A function that sometimes raises Allowed2."""

    if x:
        raise Allowed2()

def test_raises_decorator():
    """The constraint on raises_a2 has been correctly recorded."""

    assert raise_a2._raises__xc_raises == (Allowed2,)


@raises(Allowed1)
def raise_bad(x):
    """This function can raise a bad exception."""

    if x:
        raise Allowed1()
    raise Allowed2()


@raises(None)
def may_not_raise():
    """This function is not allowed to raise any exceptions, but does."""

    raise Allowed2()

def test_raise_bad():
    """Test that the may_not_raise() function works as expected."""
    with pytest.raises(BadExceptionBug):
        may_not_raise()

def test_raise_ok():
    """Test that raise_a2() works as expected."""

    with pytest.raises(Allowed2):
        raise_a2(True)

    # Does not raise...

    raise_a2(False)

    # raise_bad behaves as expected

    with pytest.raises(Allowed1):
        raise_bad(True)

    with pytest.raises(BadExceptionBug):
        raise_bad(False)


def test_try_behaviour_assumptions():
    """Test that Python except clauses work as expected."""

    x = []
    try:
        x.append('start')
        raise Allowed1()
        x.append('notreached')
    except () as e:
        raise Exception("Caught nothing")
    except Allowed1 as e:
        x.append('caught')

    assert x == ['start','caught']


#
# Set up and try the test fixture stuff
#


class LowerEx(Exception):
    """May be raised by a low level function"""
    pass


class LowerEx1(LowerEx):
    """A subclass of :class:`LowerEx`"""
    pass


class OtherEx(Exception):
    """An exception unrelated to :class:`LowerEx`"""

    pass


@raises(LowerEx,OtherEx,LowerEx1)
def lower(x):
    """Low-level function that may raise an exception."""

    if x:
        raise LowerEx()


def upper(x):
    """Upper-level function that catches an exception."""
    try:
        lower(x)
        return None
    except Exception as e:
        print("lower raised %s" % (repr(e)))
        return e

def test_raises_exception():
    """The raises_exception function generates the exceptions it is passed."""

    print("lower may raise %s" % (may_raise(lower)))

    # Pretend that the lower() function raises some different exceptions

    exceptions = [LowerEx(), LowerEx1()]

    results = []
    for _ in raises_exception(__name__+'.lower',*exceptions):
     #   print "Here we go..."
        results.append(upper(False))

    assert results == exceptions


def test_raises_exception_detects_bad_list():
    """Tests that raises_exception refuses to raise an exception
    that the target is not declared capable of raising
    """

    print("lower may raise %s" %(may_raise(lower)))

    with pytest.raises(BadExceptionsInTestBug):
        for _ in raises_exception(__name__+'.lower',Exception('bang'),LowerEx(),LowerEx1()):
            upper(False)

#
# Test awkward cases in raises_exception:
#
# Something goes wrong with the exception list
#

class UnexpectedExc(Exception):
    """
    This is raised by my fake Raiser
    to trigger some error paths
    """
    pass


class BadRaiser(object):
    """Replaces _raises.Raiser with a rogue
    implementation that always raises an unexpected
    and disallowed exception type"""

    def __init__(self):
        pass

    def configure(self, exceptions):
        pass

    def __call__(self,*args,**kwargs):
        raise UnexpectedExc()


class NonRaiser(object):
    """Replaces _raises.Raiser with a rogue
    implementation that fails to raise an exception"""

    def __init__(self):
        pass

    def configure(self, exceptions):
        pass

    def __call__(self,*args,**kwargs):
        return


def test_raises_exception_error_case():
    with patch('rjgtoys.xc.raises.Raiser',BadRaiser):

        for _ in raises_exception(__name__+'.lower',LowerEx(),LowerEx1()):
            upper(False)


def test_raises_exception_nonraising_case():

    with patch('rjgtoys.xc.raises.Raiser',NonRaiser):
        for _ in raises_exception(__name__+'.lower',LowerEx(),LowerEx1()):
            upper(False)

