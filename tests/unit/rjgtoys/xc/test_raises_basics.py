"""
Test the constraint mechanisms in _raises
"""

from rjgtoys.xc.raises import raises, may_raise, raises_exception

from rjgtoys.xc import BadExceptionBug, BadExceptionsInTestBug

import pytest
from unittest.mock import patch

class Allowed1(Exception):
    """
    First allowed exception
    """

    pass

class Allowed2(Exception):
    """
    Second allowed exception
    """

    pass

def raise_a1():
    raise Allowed1()

def test_default_may_raise():
    assert may_raise(raise_a1) == set((Exception,))

    with pytest.raises(Allowed1):
        raise_a1()

@raises(Allowed2)
def raise_a2(x):
    if x:
        raise Allowed2()

def test_raises_decorator():

    assert raise_a2._raises__xc_raises == (Allowed2,)

@raises(Allowed1)
def raise_bad(x):
    if x:
        raise Allowed1()
    raise Allowed2()

@raises(None)
def may_not_raise():
    raise Allowed2()

def test_raise_bad():
    with pytest.raises(BadExceptionBug):
        may_not_raise()

def test_raise_ok():
    with pytest.raises(Allowed2):
        raise_a2(True)

    raise_a2(False)

    with pytest.raises(Allowed1):
        raise_bad(True)

def test_try_behaviour_assumptions():

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
    if x:
        raise LowerEx()

def upper(x):
    try:
        lower(x)
    except Exception as e:
        print("lower raised %s" % (repr(e)))

def test_raises_exception():
    # FIXME: I'm not sure what this is testing!

    #print "lower may raise", may_raise(lower)

    for _ in raises_exception(__name__+'.lower',LowerEx(),LowerEx1()):
     #   print "Here we go..."
        upper(False)


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
