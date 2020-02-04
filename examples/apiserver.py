"""
A simple API server based on FastAPI, using XC exceptions.
"""

from typing import Union

from pydantic import BaseModel, Field

import fastapi

from rjgtoys.xc import Error, Title

from rjgtoys.xc.fastapi import handle_xc, APIRouter


from apierrors import *


class HelloService:

    def __init__(self, msg, app):
        self.msg = msg
        route = app.get('/hello')
        route(self.hello)

    def hello(self):
        return dict(message=self.msg)


class Result(BaseModel):

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

svc = HelloService('hello, again', router)

#
# Build the app
#

app = fastapi.FastAPI()

app.add_exception_handler(Error, handle_xc)

app.include_router(router)
