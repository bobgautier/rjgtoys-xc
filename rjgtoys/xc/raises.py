"""
Auto-document and enforce exception raising behaviour.

"""

import functools
import inspect
from dataclasses import dataclass
import jinja2

from rjgtoys import xc


@dataclass
class ExceptionInfo:
    module: str
    name: str
    qualname: str
    title: str
    isleaf: bool


class raises:
    def __init__(self, *excs):

        self._raises = tuple(self.flatten(excs))

        # Just a single None means the function may raise no exceptions at all

        if self._raises == (None,):
            self._raises = tuple()

    def __call__(self, f):

        # Generate the enforcing function

        @functools.wraps(f)
        def _f(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except self._raises:  # Allowed exceptions are just propagated
                raise
            except xc.Bug:  # Any bugs are just propagated
                raise
            except Exception as bug:
                raise xc.BadExceptionBug(raised=bug) from bug

        # Save the allowed exception list

        _f.__xc_raises = self._raises

        # Now extend its documentation

        body = self.render()

        # Figure out the indentation level of the target
        # docstring

        doc = f.__doc__ or ''

        try:
            lastline = doc.splitlines()[-1]
        except IndexError:
            lastline = ''

        indent = len(lastline) - len(lastline.lstrip())
        indent = lastline[: indent + 1]

        body = [indent + line for line in body.splitlines()]

        _f.__doc__ = doc + "\n".join(body)

        return _f

    DEFAULT_TEMPLATE = """

    Raises:

    {% for e in exceptions %}
    {% if e.isleaf %}
    :exc:`~{{e.qualname}}`
    {% else %}
    :exc:`~{{e.qualname}}` (or a subclass of it)
    {% endif %}
        {{e.title}}
    {% endfor %}

    """

    def get_template(self, name):
        """Get the template to be used here."""

        return self.undent(self.DEFAULT_TEMPLATE)

    def render_template(self, template, **args):
        """Find and render a template."""

        env = jinja2.Environment(loader=jinja2.FunctionLoader(self.get_template))

        tpl = env.get_template(template)

        return tpl.render(**args)

    def render(self):

        info = list(self.get_exception_info())

        return self.render_template('default', exceptions=info)

    def get_exception_info(self):

        exceptions = []
        for e in self._raises:
            isleaf = not e.__subclasses__()

            if isinstance(e, xc._xc._XCType):
                title = e.title
            else:
                title = e.__doc__
                if title:
                    title = title.splitlines()[0]
                else:
                    title = '(not documented)'

            module = e.__module__
            qualname = "%s.%s" % (module, e.__name__)
            yield ExceptionInfo(
                module=module,
                name=e.__name__,
                qualname=qualname,
                title=title,
                isleaf=isleaf,
            )

    @classmethod
    def flatten(cls, x):
        """Flatten a list, set or tuple (that might contain instances of those)."""
        if isinstance(x, (list, set, tuple)):
            for c in x:
                yield from cls.flatten(c)
        else:
            yield x

    @staticmethod
    def undent(text):
        """Remove indentation from some text."""

        width = None
        result = []
        for line in text.splitlines():
            if width is None:
                # Try to get the width of the indent.
                # But blank lines don't count; they
                # are just copied to the output
                undented = line.lstrip()
                if not undented:
                    result.append(undented)
                    continue
                width = len(line) - len(undented)
            line = line[width:]
            result.append(line)
        return "\n".join(result)


def may_raise(f):
    """
    Return the set of exceptions that a callable may raise.

    Returns {:class:`Exception`} if the callable has made no more
    precise declaration.
    """

    try:
        return set(getattr(f, '_raises__xc_raises'))
    except:
        return set((Exception,))


class Raiser(object):

    """A simple object used to replace a callable by
    something that will raise an exception.   It is
    constructed with an iterable collection of exceptions
    that it is to raise, and will raise one each time it is
    called.

    This could be done more simply, but this implementation
    seems to be easier to test.
    """

    def __init__(self):
        self.to_raise = iter([])

    def configure(self, exceptions):
        self.to_raise = iter(exceptions)

    def __call__(self, *args, **kwargs):
        raise next(self.to_raise)


def raises_exception(name, *exceptions):
    """
    Testing support: replaces a callable by something that raises each
    exception in turn.  The exceptions you provide must be instances
    of the exception(s) that the object is allowed to raise.

    The list of exceptions must be passed in cases where the
    named callable names classes of exception (in that case,
    the exceptions list must list at least one subclass of
    each class of exception that the callable may raise).

    TODO: clarify the above!
    """

    from unittest.mock import patch

    raiser = Raiser()

    p = patch(name, raiser)

    f = p.get_original()[0]

    allowed = may_raise(f)

    # Are we testing the right exceptions?
    # by default, check all that are allowed

    if not exceptions:
        exceptions = allowed
    else:
        a = tuple(allowed)
        notallowed = [e for e in exceptions if not isinstance(e, a)]

        if notallowed:
            raise xc.BadExceptionsInTestBug(name=name, exceptions=notallowed)

    raiser.configure(exceptions)

    # Are we testing all the cases?

    tested = set(c for e in exceptions for c in inspect.getmro(type(e)))

    untested = set(allowed).difference(tested)

    if untested:
        untested = [u.__name__ for u in untested]
        print("%s is not being tested when raising %s" % (name, untested))

    with p as q:

        # check that 'exceptions' is valid and covers all the cases

        for e in exceptions:
            # The relevant name of the type for e is the one that
            # matches an entry in the allowed list
            t = set(inspect.getmro(type(e)))
            t.intersection_update(allowed)

            # If we found no 'names', then this exception is not of a
            # type in the allowed set, i.e. it's not allowed

            # At this stage, I don't think that can happen:
            # we've already checked that all the exceptions
            # in the exceptions list are allowed for the target
            # callable.

            assert t, (
                "Encountered a bad exception %s"
                "despite pre-validation of the list" % (repr(e))
            )

            # If the exception matches more than one item in the allowed
            # set, then the allowed set has a redundancy.
            #   This should have been caught earlier, for example
            #   when creating the original allowed set.

            #
            n = ",".join(sorted([c.__name__ for c in t]))
            print("Testing when %s raises %s: %s" % (name, n, repr(e)))
            yield
