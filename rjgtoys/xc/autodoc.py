
from typing import Any, get_type_hints


import json


from sphinx.ext.autodoc import ClassDocumenter

from sphinx_autodoc_typehints import format_annotation

from rjgtoys.xc._xc import XC

class XCDocumenter(ClassDocumenter):
    """
    Specialized ClassDocumenter subclass for XC exceptions.
    """
    objtype = 'xc'
    directivetype = 'exception'
    member_order = 10

    # needs a higher priority than ClassDocumenter and ExceptionDocumenter
    priority = 15

    @classmethod
    def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any
                            ) -> bool:
        return isinstance(member, type) and issubclass(member, XC)


    def get_base_description(self):

        if not hasattr(self.object, '__bases__') or not len(self.object.__bases__):
            print("Could not identify bases for %s.%s" % (self.object.__module__, self.object.__name__))
            return ""

        bases = [':class:`%s.%s`' % (b.__module__, b.__name__)
                    for b in self.object.__bases__]
        return ', '.join(bases)

    def generate(self, more_content: Any = None, real_modname: str = None,
                 check_module: bool = False, all_members: bool = False) -> None:
        """Generate reST for the object given by *self.name*, and possibly for
        its members.

        If *more_content* is given, include that content. If *real_modname* is
        given, use that module name to find attribute docs. If *check_module* is
        True, only generate if the object is defined in the module name it is
        imported from. If *all_members* is True, document all members.
        """
        if not self.parse_name():
            # need a module to import
            logger.warning(
                __('don\'t know which module to import for autodocumenting '
                   '%r (try placing a "module" or "currentmodule" directive '
                   'in the document, or giving an explicit module name)') %
                self.name, type='autodoc')
            return

        # now, import the module and get object to document
        if not self.import_object():
            return

        schema = self.object._model.schema()

        try:
            hints = get_type_hints(self.object._model)
        except Exception as e:
            print("Get type hints for %s: %s" % (self.fullname, e))
            hints = {}

        source = "description of %s" % (self.object_name)

        sig = "(%s)" % (", ".join(schema['properties'].keys()))

        self.add_directive_header(sig)

        self.add_line('', source)

        indent = self.indent
        try:
            self.indent += '   '

            for (i, line) in enumerate(schema['description'].splitlines()):
                self.add_line(line.strip(), source, i)

            # Always do 'show-inheritance'

            bases = self.get_base_description()

            if bases:
                self.add_line('', source)
                self.add_line("A subclass of %s" % (bases), source)

            self.add_line('', source)

            source = self.get_sourcename()

            for (pname, ptype) in schema['properties'].items():
                hint = hints.get(pname,'')
                if hint:
                    hint = format_annotation(hint)
                else:
                    hint = '(unspecified)'

                self.add_line(':param %s: %s' % (pname, ptype['title']), source)
                self.add_line(':type %s: %s' % (pname, hint), source)

                self.add_line('', source)

            self.add_line('Each parameter defines an attribute of the same name.', source)
            self.add_line('', source)

            # Add the attributes

            self.add_line('Properties (read-only)', source)


            for name in ('typename', 'title', 'detail', 'status'):
                self.add_line(
                    '  :py:attr:`%s` = %s' % (name,repr(getattr(self.object, name))),
                    source
                )
                self.add_line('', source)

            self.add_line((
                'For more information about the above properties'
                ' please refer to the description of the base class :py:class:`~rjgtoys.blobs.xc.XC`.'
                ),
                source
            )

        finally:
            self.indent = indent

        #return

        # DEBUG: dump our output

        for line in self.directive.result:
            print("RESULT: %s" % (line))


def setup(app):
    app.add_autodocumenter(XCDocumenter)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
