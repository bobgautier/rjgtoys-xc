"""
Auto-document exception raising behaviour.

"""

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
        self._raises = self.flatten(excs)

    def __call__1(self, f):
        body = ["","Raises:",""]

        for e in self._raises:
            leaf = not e.__subclasses__()

            if isinstance(e, xc._xc._XCType):
                title = e.title
            else:
                title = e.__doc__
                if title:
                    title = title.splitlines()[0]
                else:
                    title = '(not documented)'

            if leaf:
                comment=""
            else:
                comment=" (or a subclass of it)"

            body.extend([
            "- :exc:`%s.%s`%s: %s" % (e.__module__,e.__name__,comment, title),
            ""
            ])

        body.append("")

        # Figure out the indentation level of the target
        # docstring

        doc = f.__doc__ or ''

        lastline = doc.splitlines()[-1]

        indent = len(lastline) - len(lastline.lstrip())
        indent = lastline[:indent+1]

        body = [ indent+line for line in body ]

        f.__doc__ += "\n".join(body)

        return f


    def __call__(self, f):

        body = self.render()

        # Figure out the indentation level of the target
        # docstring

        doc = f.__doc__ or ''

        lastline = doc.splitlines()[-1]

        indent = len(lastline) - len(lastline.lstrip())
        indent = lastline[:indent+1]

        body = [ indent+line for line in body.splitlines() ]

        f.__doc__ += "\n".join(body)

        return f


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

        env = jinja2.Environment(
            loader=jinja2.FunctionLoader(self.get_template)
        )

        tpl = env.get_template(template)

        return tpl.render(
                **args
            )

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
                isleaf=isleaf
            )

    @classmethod
    def flatten(cls, x):
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
