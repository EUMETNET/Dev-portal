"""
Defines the FastAPI app.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from app.exceptions import http_exception_handler, general_exception_handler
from app.routers import apikey
from app.config import settings

config = settings()

app = FastAPI()

# Middleware
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:3002",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Routers
app.include_router(apikey.router)


# Start the server using poetry script
def start() -> None:
    """
    Start the Uvicorn server
    """
    uvicorn.run("app.main:app", port=config.port, reload=True)
