import logging
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.admin import admin_router_readonly, health_router, schema_router_readonly
from app.config.config import config
from app.entrypoints.web import chat_router_readonly
from models.db import init_db
from models.redis import init_redis

# init logger
logger = logging.getLogger(__name__)

if config.sentry_dsn:
    sentry_sdk.init(
        dsn=config.sentry_dsn,
        sample_rate=config.sentry_sample_rate,
        traces_sample_rate=config.sentry_traces_sample_rate,
        profiles_sample_rate=config.sentry_profiles_sample_rate,
        environment=config.env,
        release=config.release,
        server_name="intent-readonly",
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db(**config.db)

    # Initialize Redis if configured
    if config.redis_host:
        await init_redis(
            host=config.redis_host,
            port=config.redis_port,
        )

    logger.info("Readonly API server starting")
    yield
    logger.info("Readonly API server shutting down")


app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(health_router)
app.include_router(admin_router_readonly)
app.include_router(schema_router_readonly)
app.include_router(chat_router_readonly)
