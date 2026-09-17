import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.Core.database import Base, engine
from app.Core.logger import logger
from app.Routers.user_router import router as user_router


app = FastAPI()

app.include_router(user_router)

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