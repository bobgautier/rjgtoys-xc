"""
A simple API server based on FastAPI, using XC exceptions.
"""

from pydantic import BaseModel

import fastapi

from rjgtoys.xc import Error

from rjgtoys.xc.fastapi import handle_xc, APIRouter


from apierrors import *


class Result(BaseModel):
    """This is the model for operation result return."""

    op: str
    a: float
    b: float
    result: float

#
# Create all the routes
#

router = APIRouter()

@router.get('/sum')
def sumit(a: int, b: int) -> Result:
    return Result(op='sum', a=a, b=b, result=a+b)

@router.get('/div')
def quotient(a: float, b: float) -> Result:
    try:
        return Result(op='div', a=a, b=b, result=a/b)
    except Exception as e:
        raise OpError(op='div', error= str(e), a=a, b=b)


app = fastapi.FastAPI()

app.add_exception_handler(Error, handle_xc)

app.include_router(router)
