"""

Helpers for starlette-based API servers.

"""

from typing import *

from pydantic import BaseModel

from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.routing import BaseRoute
from starlette.types import ASGIApp


from rjgtoys.xc import Error, Title


async def handle_xc(request: Request, exc: Error):

    #    print("Handing exception %s" % (exc))
    return JSONResponse(
        status_code=exc.status,
        content=exc.to_dict(),
        media_type='application/problem+json',
    )
