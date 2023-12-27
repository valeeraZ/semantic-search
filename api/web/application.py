from importlib import metadata

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import UJSONResponse
from fastapi_pagination import add_pagination

from api.web.api import api_router
from api.web.lifetime import lifespan


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        title="semantic search",
        version=metadata.version("api"),
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
        lifespan=lifespan,
    )

    # Adds startup and shutdown events.

    origins = [
        "http://localhost",
        "http://localhost:3000",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    app.add_middleware(CorrelationIdMiddleware)

    add_pagination(app)

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")
    # # add exception handlers
    # app.add_exception_handler(NotFoundError, not_found_error_handler)
    # app.add_exception_handler(NotCreatedError, not_created_error_handler)
    # app.add_exception_handler(NotUpdatedError, not_updated_error_handler)
    # app.add_exception_handler(NotDeletedError, not_deleted_error_handler)

    return app
