"""Launcher: run with `uvicorn main:app`."""
import logging

import uvicorn
from configs.cpy import settings
from fastapi import FastAPI, APIRouter, Depends
from middleware.fastapi_plugin import basic_authenticate, LoggingRequestMiddleware
from starlette.middleware.cors import CORSMiddleware

from fastapi_router.admin import admin
from fastapi_router.api import r1

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

context_path = settings.server_context_path
app = FastAPI(
    docs_url=f'{context_path}/docs',
    redoc_url=f'{context_path}/redoc',
    openapi_url=f'{context_path}/openapi.json',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.add_middleware(BasicAuthMiddleware)
app.add_middleware(LoggingRequestMiddleware )

context_router = APIRouter(prefix=context_path, dependencies=[Depends(basic_authenticate)])

context_router.include_router(admin, prefix="/admin/v1")
context_router.include_router(r1, prefix="/r1")

app.include_router(context_router)

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=9003)
