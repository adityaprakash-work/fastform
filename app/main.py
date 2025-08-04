"""Entrypoint."""

from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from guidance.models import Model, OpenAI
from sqlalchemy.engine.base import Engine
from sqlmodel import SQLModel, create_engine

from .api import v1_router
from .config import APIKeys, AppConfig, DatabaseConfig
from .models import Annotation, Message, User

app_config = AppConfig()
keys = APIKeys()
db_settings = DatabaseConfig()


def setup_cors(app: FastAPI) -> FastAPI:
    """Setup CORS middleware.

    Args:
        app (FastAPI): The FastAPI application instance.
    Returns:
        FastAPI: The FastAPI application instance with CORS middleware configured.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_config.cors_allow_origins,
        allow_credentials=app_config.cors_allow_credentials,
        allow_methods=app_config.cors_allow_methods,
        allow_headers=app_config.cors_allow_headers,
    )
    return app


def init_models() -> dict[str, Model]:
    """Load models based on the application settings.

    Returns:
        dict[str, Model]: A dictionary mapping model names to their instances.
    """
    models = {}

    if keys.openai:
        models["gpt-4o-mini"] = OpenAI(model="gpt-4o-mini", api_key=keys.openai)

    return models


async def init_db() -> Engine | None:
    """Initialize the database connection and create the necessary tables.

    Returns:
        Engine | None: The SQLAlchemy engine connected to the database, or None if
            connection fails.
    """
    try:
        db_url = db_settings.url
        if not db_url:
            print("Warning: Database URL is not set. Skipping database initialization.")
            return None

        engine = create_engine(db_url)
        # Test the connection
        engine.connect().close()

        SQLModel.metadata.create_all(
            engine,
            tables=[Message.__table__, Annotation.__table__, User.__table__],
        )
        print(f"Database initialized successfully with URL: {db_url}")
        return engine
    except Exception as e:
        print(f"Warning: Failed to initialize database: {e}")
        print("Application will continue without database functionality.")
        return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager.

    This function initializes the application state and cleans up resources
    when the application is shutting down.

    Args:
        app (FastAPI): The FastAPI application instance.
    Yields:
        None: This function does not return any value, but it yields control
        to the application during its lifespan.
    """
    app.state.models = init_models()
    app.state.db_engine = await init_db()

    try:
        yield
    finally:
        if hasattr(app.state, "db_engine") and app.state.db_engine:
            del app.state.db_engine
        if hasattr(app.state, "models"):
            del app.state.models


docs_enabled = app_config.docs_enabled

app = FastAPI(
    title=app_config.name,
    version=app_config.version,
    lifespan=lifespan,
    docs_url="/docs" if docs_enabled else None,
    redoc_url="/redoc" if docs_enabled else None,
    openapi_url="/openapi.json" if docs_enabled else None,
)
app = setup_cors(app)
if not app_config.dev_mode:
    # TODO: Add security middleware for production
    secure_router = APIRouter()
else:
    secure_router = APIRouter()
secure_router.include_router(v1_router)
app.include_router(secure_router)
