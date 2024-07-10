import os
import logging
import sys
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.projects import project_routes
from app.waypoints import waypoint_routes
from fastapi.responses import RedirectResponse, JSONResponse
from app.users import oauth_routes
from app.users import user_routes
from app.tasks import task_routes
from loguru import logger as log
from fastapi.templating import Jinja2Templates


root = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory="templates")


class InterceptHandler(logging.Handler):
    """Intercept python standard lib logging."""

    def emit(self, record):
        """Retrieve context where the logging call occurred.

        This happens to be in the 6th frame upward.
        """
        logger_opt = log.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelno, record.getMessage())


def get_logger():
    """Override FastAPI logger with custom loguru."""
    # Hook all other loggers into ours
    logger_name_list = [name for name in logging.root.manager.loggerDict]
    for logger_name in logger_name_list:
        logging.getLogger(logger_name).setLevel(10)
        logging.getLogger(logger_name).handlers = []
        if logger_name == "sqlalchemy":
            # Don't hook sqlalchemy, very verbose
            continue
        if logger_name == "urllib3":
            # Don't hook urllib3, called on each OTEL trace
            continue

        if logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"]:
            logging.getLogger(logger_name).addHandler(InterceptHandler())

        if "." not in logger_name:
            logging.getLogger(logger_name).addHandler(InterceptHandler())

    log.remove()
    log.add(
        sys.stderr,
        level=settings.LOG_LEVEL,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} "
            "| {name}:{function}:{line} | {message}"
        ),
        enqueue=True,  # Run async / non-blocking
        colorize=True,
        backtrace=True,  # More detailed tracebacks
        catch=True,  # Prevent app crashes
    )


def get_application() -> FastAPI:
    """Get the FastAPI app instance, with settings."""
    _app = FastAPI(
        title=settings.APP_NAME,
        description="HOTOSM Drone Tasking Manager",
        license_info={
            "name": "GPL-3.0-only",
            "url": "https://raw.githubusercontent.com/hotosm/fmtm/main/LICENSE.md",
        },
        debug=settings.DEBUG,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        redoc_url="/api/redoc",
    )

    # Set custom logger
    _app.logger = get_logger()

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.EXTRA_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition"],
    )

    _app.include_router(project_routes.router)
    _app.include_router(waypoint_routes.router)
    _app.include_router(user_routes.router)
    _app.include_router(oauth_routes.router)
    _app.include_router(task_routes.router)

    return _app


api = get_application()


@api.get("/")
async def home(request: Request):
    try:
        """Return Frontend HTML"""
        return templates.TemplateResponse(
            name="index.html", context={"request": request}
        )
    except Exception:
        """Fall back if tempalate missing. Redirect home to docs."""
        return RedirectResponse(f"{settings.API_PREFIX}/docs")


known_browsers = ["Mozilla", "Chrome", "Safari", "Opera", "Edge", "Firefox"]


@api.exception_handler(404)
async def custom_404_handler(request: Request, _):
    """Return Frontend HTML or throw 404 Response on 404 requests."""
    try:
        query_params = dict(request.query_params)
        user_agent = request.headers.get("User-Agent", "")
        format = query_params.get("format")
        is_browser = any(browser in user_agent for browser in known_browsers)
        if format == "json" or not is_browser:
            return JSONResponse(status_code=404, content={"detail": "Not found"})
        return templates.TemplateResponse(
            name="index.html", context={"request": request}
        )

    except Exception:
        """Fall back if tempalate missing. Redirect home to docs."""
        return JSONResponse(status_code=404, content={"detail": "Not found"})
