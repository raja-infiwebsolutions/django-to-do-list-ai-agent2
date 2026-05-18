from typing import Any, Optional, Dict
from django.http import JsonResponse
from django.core.exceptions import ValidationError, PermissionDenied
from django.http import Http404
import logging

logger = logging.getLogger(__name__)


def success_response(data: Any = None, message: str = "Success", status: int = 200) -> JsonResponse:
    """Return a standardized JSON success response.

    Structure:
    {
        "success": True,
        "message": "...",
        "data": { ... } | [] | null
    }
    """
    payload: Dict[str, Any] = {"success": True, "message": message, "data": data}
    return JsonResponse(payload, status=status)


def error_response(message: str = "An error occurred", errors: Optional[Any] = None, status: int = 400) -> JsonResponse:
    """Return a standardized JSON error response.

    Structure:
    {
        "success": False,
        "message": "...",
        "errors": { ... } (optional)
    }
    """
    payload: Dict[str, Any] = {"success": False, "message": message}
    if errors is not None:
        payload["errors"] = errors
    return JsonResponse(payload, status=status)


def handle_exception(exc: Exception) -> JsonResponse:
    """Map common Django exceptions to standardized JSON responses.

    This helper can be used in views to ensure consistent error shapes.
    """
    # Django ValidationError -> 400
    if isinstance(exc, ValidationError):
        # Prefer structured attributes if available, fallback to string
        details = getattr(exc, 'message_dict', None) or getattr(exc, 'messages', None) or str(exc)
        return error_response(message="Validation error", errors=details, status=400)

    # PermissionDenied -> 403
    if isinstance(exc, PermissionDenied):
        return error_response(message="Permission denied", status=403)

    # Not found -> 404
    if isinstance(exc, Http404):
        return error_response(message="Not found", status=404)

    # Fallback -> 500 without leaking internals
    logger.exception("Unhandled exception: %s", exc)
    return error_response(message="Internal server error", status=500)
