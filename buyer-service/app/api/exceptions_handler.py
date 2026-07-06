"""Global exception handlers mapped to HTTP responses."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import KisanGPTException


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(KisanGPTException)
    async def kisangpt_exception_handler(
        request: Request, exc: KisanGPTException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.http_status,
            content={
                "success": False,
                "error_code": exc.error_code,
                "message_en": exc.message_en,
                "message_te": exc.message_te,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message_en": "Request validation failed.",
                "message_te": "అభ్యర్థన ధృవీకరణ విఫలమైంది.",
                "details": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "INTERNAL_ERROR",
                "message_en": "An internal server error occurred.",
                "message_te": "అంతర్గత సర్వర్ లోపం సంభవించింది.",
            },
        )
