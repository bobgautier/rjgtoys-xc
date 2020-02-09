To-do List
==========

Many more tests.  In particular, make sure that intermediate classes of exceptions work properly.

Documentation generation for grouping classes; list the subclasses.

Better construction of the error response schema:

1. Don't assume everything uses 400
2. Fill in the schema for the 'content'

Additional problem report fields, such as:

- Timestamp
- Origin (e.g. host, PID)
- Trace id/correlation id of some kind (UUID)

Provide endpoints that can do something useful with the 'type' and 'instance' attributes
of a problem report.

Support computed or implied attributes of an exception (construction-time method).



