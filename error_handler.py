
from dataclasses import dataclass
from typing import Optional

from logger_config import get_logger

logger = get_logger(__name__)


@dataclass
class AppError:
    """A safe error that can be displayed to the user."""

    message: str
    code: str = "APPLICATION_ERROR"
    retryable: bool = False


def handle_exception(
    exc: Exception,
    *,
    operation: str,
    retryable: bool = False,
) -> AppError:
    """
    Log technical details and return a safe user-facing error.

    Do not pass passwords, tokens, resume text, or private answers
    in the operation string.
    """

    logger.error(
        "Operation failed: %s; error_type=%s",
        operation,
        type(exc).__name__,
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    return AppError(
        message=(
            "The operation could not be completed. "
            "Please try again."
        ),
        code="OPERATION_FAILED",
        retryable=retryable,
    )


def safe_error_message(
    exc: Exception,
    *,
    operation: str,
) -> str:
    """Return a safe message without exposing internal details."""

    return handle_exception(
        exc,
        operation=operation,
    ).message
