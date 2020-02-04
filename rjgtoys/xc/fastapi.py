"""

Helpers for starlette-based API servers.

"""

from typing import Union

from pydantic import BaseModel

from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.routing import BaseRoute
from starlette.types import ASGIApp

from fastapi import routing, params
from fastapi.encoders import DictIntStrAny, SetIntStr


# This is just a convenience so that clients can avoid
# importing both helper packages

from rjgtoys.xc.starlette import *

from rjgtoys.xc import Error

# Keep this for reference

class ErrorResponse(BaseModel):
    """Document returned with an error."""

    type: str = Title("Name of the error class")
    title: str = Title("Readable description of the error class")
    instance: str = Title("URI for this instance of the error")
    detail: str = Title("Description of this instance of the error")
    status: int = Title("HTTP status code")
    content: dict = Title("Content of the error - depends on type")


ErrorResponses = {
    400: { 'model': ErrorResponse }
}


class APIRoute(routing.APIRoute):

    def __init__(
        self,
        path: str,
        endpoint: Callable,
        *,
        response_model: Type[Any] = None,
        status_code: int = 200,
        tags: List[str] = None,
        dependencies: Sequence[params.Depends] = None,
        summary: str = None,
        description: str = None,
        response_description: str = "Successful Response",
        responses: Dict[Union[int, str], Dict[str, Any]] = None,
        deprecated: bool = None,
        name: str = None,
        methods: Optional[Union[Set[str], List[str]]] = None,
        operation_id: str = None,
        response_model_include: Union[SetIntStr, DictIntStrAny] = None,
        response_model_exclude: Union[SetIntStr, DictIntStrAny] = set(),
        response_model_by_alias: bool = True,
        response_model_exclude_unset: bool = False,
        include_in_schema: bool = True,
        response_class: Optional[Type[Response]] = None,
        dependency_overrides_provider: Any = None,
        callbacks: Optional[List["APIRoute"]] = None,
    ) -> None:
        try:
            rtype = endpoint.__annotations__['return']
        except:
            rype = response_model

        responses = responses or {}
        combined_responses = { **responses, **ErrorResponses }

        super().__init__(
            path=path,
            endpoint=endpoint,
            status_code=status_code,
            tags=tags,
            dependencies=dependencies,
            summary=summary,
            description=description,
            response_description=response_description,
            responses=combined_responses,
            deprecated=deprecated,
            name=name,
            methods=methods,
            operation_id=operation_id,
            response_model_include=response_model_include,
            response_model_exclude=response_model_exclude,
            response_model_by_alias=response_model_by_alias,
            include_in_schema=include_in_schema,
            response_class=response_class,
            dependency_overrides_provider=dependency_overrides_provider,
            callbacks=callbacks
        )


class APIRouter(routing.APIRouter):
    def __init__(
        self,
        routes: List[BaseRoute] = None,
        redirect_slashes: bool = True,
        default: ASGIApp = None,
        dependency_overrides_provider: Any = None,
        route_class: Type[APIRoute] = APIRoute,
        default_response_class: Type[Response] = None,
    ) -> None:
        super().__init__(
            routes=routes,
            redirect_slashes=redirect_slashes,
            default=default,
            dependency_overrides_provider=dependency_overrides_provider,
            route_class=route_class,
            default_response_class=default_response_class
        )
