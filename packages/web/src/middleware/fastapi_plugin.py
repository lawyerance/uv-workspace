import base64
import logging
import secrets
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from starlette import status
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.types import ASGIApp

USER_DATABASE = {
    'admin': 'admin',
    'user': 'user',
}
security = HTTPBasic()


def basic_authenticate(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    """
    Dependency function to verify the incoming Basic Auth credentials.
    """
    # Look up user in database
    correct_password = USER_DATABASE.get(credentials.username)

    # Check if user exists
    if not correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    # Use secrets.compare_digest to defend against timing attacks
    is_correct_username = secrets.compare_digest(credentials.username, credentials.username)
    is_correct_password = secrets.compare_digest(credentials.password, correct_password)

    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


class BasicAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        basic_auth = request.headers.get("Authorization")
        if basic_auth and basic_auth.startswith("Basic "):
            username, password = base64.b64decode(basic_auth.split('')[1]).split(' ')
            if username != "admin" and password != "admin":
                return await call_next(request)
            else:
                return JSONResponse(status_code=401, content={"message": "Invalid username or password"})
        else:
            return JSONResponse({"error": "Invalid Authorization Header"}, status_code=401)


class LoggingRequestMiddleware(BaseHTTPMiddleware):
    _logger: logging.Logger

    def __init__(self, app: ASGIApp, logger: logging.Logger | None = None):
        super().__init__(app)
        self._logger = logger if logger else logging.getLogger(__name__)

    async def dispatch(self, request: Request, call_next) -> Response:
        url: str = f'{request.url.path}?{request.url.query}' if request.url.query else request.url.path
        self._logger.info(f'--> {request.method} {url}')
        for header in request.headers.items():
            self._logger.info(f'--> {header[0]}: {header[1]}')
        response = await call_next(request)
        self._logger.info('')
        self._logger.info(f'<-- {response.status_code}')
        for (k, v) in response.headers.items():
            self._logger.info(f'<-- {k}: {v}')
        return response
