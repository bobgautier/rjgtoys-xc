Using XC in Web APIs
====================

Background
----------


HTTP as Transport: status codes
*******************************

I've always had a bit of a problem deciding how best to return errors from HTTP REST APIs.

On the one
hand, HTTP offers a wide variety of well defined status codes that are not hard to fit to the conditions
that many APIs will need to signal.

On the other, I'd always suspected that do use HTTP status codes to signal API issue was to confuse 'transport
errors' (HTTP) with 'application errors' (exceptions).

This dilemma is covered very well by Guy Levin in this blog post: http://blog.restcase.com/rest-api-error-codes-101/

He gives the example of using status code 404 to indicate (API) 'resource not found'.  That seems a natural thing to
do, but it creates the risk of confusion or ambiguity in the response to a poorly formed or mis-spelled API endpoint
URL, which might also generate a 404 response.

So, Guy Levin (and I) recommend using a small subset of HTTP status codes for 'API errors', and leaving most of
them to indicate 'tranport errors'; 404 will mean an endpoint was not found, rather than a resource not found,
for example.


RFC7807 Problem Detail Reports
******************************

This post about `Best Practices for REST API Error Handling`_ comes to a similar conclusion about how to use status
codes, and goes on to talk about how to construct a response body when signalling an error.  It introduced me
to RFC7807_, which defines a standard way to describe 'problem reports' in HTTP APIs.

.. _Best Practices for REST API Error Handling: https://www.baeldung.com/rest-api-error-handling-best-practices

.. _RFC7807: https://tools.ietf.org/html/rfc7807

RFC7807 defines 'problem details objects' that might be represented either in XML or JSON, that must
contain at least the following fields (the following is an abbreviated form of the text from the RFC):

type (string)
  A URI that identifies the  problem type.  RFC7807 encourages that, when
  dereferenced, it provide human-readable documentation for the
  problem type.

title (string)
   A short, human-readable summary of the problem
   type.  It should describe the type of the problem, not the particular case being signalled.
   So "File does not exist" rather than "File /etc/foobar does not exist"

status (number)
   The HTTP status code that was returned with this problem report.

detail (string)
   A human-readable explanation specific to this occurrence of the problem (compare 'title', above).

instance (string)
   A URI that identifies the specific occurrence of the problem; it  may yield further
   information if dereferenced but need not.

In addition to the above required fields, RFC7807 permits problem detail reports to contain any other fields
that an API may require in order to describe the error adequately.

So a 'file not found' report might, for example, include a 'path' attribute that specifies the path that
was not found.

The interpretation of RFC7807 in XC
-----------------------------------

XC currently implements a fairly loose interpretation of RFC7807, for the `type` and `instance` fields.

This is how XC produces the problem report fields:

type
  By default this is just the name of the exception class.  This meets the letter of RFC7807
  because it permits relative URIs, and the class name could indeed be a relative URI, or at
  least could easily be converted into one just before encoding the problem report for transport.

  XC does not currently provide any support for building a service that would allow
  these URIs to be dereferenced to produce further documentation as suggested by RFC7807

title
  This is a one line string provided in the exception declaration, often derived from the
  docstring.

status
  This status code is provided in the declaration, and defaults to 400.

detail
  The exception declaration includes a format template that is used to produce the RFC7807 detail string.

instance
  This too is permitted to be a relative URI, but this URI has to describe the particular instance of
  the exception.   The current implementation uses the `type` field, and appends to it a query string
  containing all the constructor parameters of the exception, so that in principle at least, the
  exception could be reconstructed from the 'instance' URI.

  In the current version of XC, 'instance' is never defined explicitly.

  XC does not currently provide any support for building a service that could dereference these URIs
  into anything useful.

API-specific fields
-------------------

RFC7807 permits the basic problem report schema describe above to be extended with additional
application- or problem-specific fields.

A natural use for this feature would be to permit exception attributes to be conveyed as attributes
of the problem report.

XC does this, but it wraps the exception attributes in a new JSON object and attaches that object
to the problem report as the 'content' field.

As a result, all XC-generated problem reports conform to the same top-level schema (they all
add a single object-valued field, 'content', to the set defined by RFC7807).


Serialisation and Deserialisation
---------------------------------

An XC exception can be converted into an RFC7807 problem report by calling its :meth:`to_dict` method
and encoding the result in JSON.

An incoming RFC7807 problem report (in JSON) can be converted back into the corresponding XC exception
by parsing the problem report and passing the resulting `dict` object to :meth:`XC.Error.from_obj`.


FastAPI and Starlette integration
---------------------------------

XC offers some basic support for writing FastAPI servers that convert XC exceptions into
HTTP status codes and JSON payloads.

FastAPI is built on top of Starlette, and the XC support is currently split into two modules
to reflect the possibility that Starlette might be used without FastAPI.

I describe the integration by means of a simple example REST API server and client.

The Example API
***************

This example API offers two functions:

1. sum
   Adds two numbers, 'a' and 'b' and returns their sum.
2. div
   Divides operand 'a' by operand 'b' and returns the result.
   If b is zero, returns an 'OpError' exception.

Error definition
****************

The error that can be returned is defined in a module that will be imported by both server and client:

.. literalinclude:: ../../examples/apierrors.py

In the XC sources, this is `examples/apierrors.py`

Server
******

The full text of the server can be found in the XC sources at `examples/apiserver.py`.

It uses two components provided by :mod:`rjgtoys.xc.fastapi`:

The class `APIRouter` replaces the default :class:`fastapi.APIRouter` and simplifies declaration of
route endpoints by using the declared return type of the target function as the response type::

    # router = rjgtoys.xc.fastapi.APIRouter()

    @router.get('/div')
    def quotient(a: float, b: float) -> Result:
        try:
            return Result(op='div', a=a, b=b, result=a/b)
        except Exception as e:
            raise OpError(op='div', error= str(e), a=a, b=b)


The function :func:`rjgtoys.XC.fastapi.handle_xc` can be installed as an exception handler for all
:class:`rjgtoys.xc.Error` exceptions, and will convert them into suitable HTTP responses that
include the exception encoded as an RFC7807 problem report::

    import fastapi
    from rjgtoys.xc import Error
    from rjgtoys.xc.fastapi import handle_xc

    app = fastapi.FastAPI()

    app.add_exception_handler(Error, handle_xc)

As a result, there is no need for service endpoint functions to include top-level exception handlers; any
exceptions that are raised as a result of request handling are returned to the caller encoded as
problem reports.

The server is run like this::

   cd examples
   python -m uvicorn -m apiserver:app

Client
******

The client code is in the XC sources as `examples/apiclient.py`.

Most of the code is concerned with parsing command line arguments, but the main body of the client
is this method::

    def get(self, op, **params):

        url = f"{self.service}{op}"
        r = requests.get(url, params=params)

        if r.status_code == 400:
            raise Error.from_obj(r.json())

        r.raise_for_status()

        return r.json()['result']

This performs an HTTP GET to the API endpoint, and if it receives a 400 status code, converts the
problem report into an exception, and raises it.

If any other (HTTP transport) error is returned, that too is converted into an exception using the
usual :mod:`requests` method.

Finally, the (success) response is parsed and the 'result' member is returned.

The client is run like this::

    $ python3 apiclient.py -h
    usage: example API client [-h] [--a A] [--b B] [--service SERVICE] {sum,div}

    positional arguments:
      {sum,div}          What to do

    optional arguments:
      -h, --help         show this help message and exit
      --a A              First parameter
      --b B              Second parameter
      --service SERVICE  URL of service
    $ python3 apiclient.py sum --a 1 --b 3
    4.0
    $ python3 apiclient.py div --a 2 --b 1
    2.0
    $ python3 apiclient.py div --a 2 --b 0
    Op div(a=2.0,b=0.0) failed: float division by zero

Note that the message printed in the final case is consistent with the declaration of the :exc:`OpError` exception.
