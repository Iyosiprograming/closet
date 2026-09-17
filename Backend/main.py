from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.Core.database import Base, engine
from app.Core.logger import logger
from app.Routers.clothe_router import router as clothe_router
from app.Routers.user_router import router as user_router


# Create images directory if it doesn't exist
IMAGE_DIR = Path("images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)


app = FastAPI()


# Serve uploaded images
app.mount(
    "/images",
    StaticFiles(directory=IMAGE_DIR),
    name="images",
)


# Routers
app.include_router(user_router)
app.include_router(clothe_router)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    logger.info("Starting application...")

    Base.metadata.create_all(bind=engine)

    logger.info("Database initialized")
    logger.info("Application started successfully")


@app.on_event("shutdown")
def shutdown():
    logger.info("Shutting down application...")
    logger.info("Application stopped")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )

