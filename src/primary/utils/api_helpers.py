"""
API Response Helpers for Huntarr-2
Standardized JSON responses for Flask routes.
"""
from flask import jsonify
from functools import wraps
import logging
import traceback

logger = logging.getLogger("Huntarr-2.API")


def api_success(data=None, message=None, status=200):
    """
    Return a successful API response.
    
    Args:
        data: Response data (dict, list, or None)
        message: Optional success message
        status: HTTP status code (default 200)
    
    Returns:
        Flask Response with JSON body
    """
    response = {"success": True}
    if data is not None:
        response["data"] = data
    if message:
        response["message"] = message
    return jsonify(response), status


def api_error(message, status=400, details=None):
    """
    Return an error API response.
    
    Args:
        message: Error message
        status: HTTP status code (default 400)
        details: Optional additional error details
    
    Returns:
        Flask Response with JSON body
    """
    response = {
        "success": False,
        "error": message
    }
    if details:
        response["details"] = details
    return jsonify(response), status


def api_not_found(resource="Resource"):
    """Return a 404 not found response."""
    return api_error(f"{resource} not found", status=404)


def api_unauthorized(message="Unauthorized"):
    """Return a 401 unauthorized response."""
    return api_error(message, status=401)


def api_forbidden(message="Forbidden"):
    """Return a 403 forbidden response."""
    return api_error(message, status=403)


def api_validation_error(message, fields=None):
    """Return a 422 validation error response."""
    return api_error(message, status=422, details={"fields": fields} if fields else None)


def api_server_error(message="Internal server error"):
    """Return a 500 server error response."""
    return api_error(message, status=500)


def handle_api_errors(f):
    """
    Decorator to catch and handle exceptions in API routes.
    
    Usage:
        @app.route('/api/example')
        @handle_api_errors
        def example():
            # If this raises, returns proper JSON error
            return api_success({"key": "value"})
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.warning(f"Validation error in {f.__name__}: {e}")
            return api_validation_error(str(e))
        except PermissionError as e:
            logger.warning(f"Permission denied in {f.__name__}: {e}")
            return api_forbidden(str(e))
        except FileNotFoundError as e:
            logger.warning(f"Not found in {f.__name__}: {e}")
            return api_not_found(str(e))
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {e}\n{traceback.format_exc()}")
            return api_server_error(str(e))
    return wrapper


# Pagination helper
def paginate(items, page=1, per_page=20):
    """
    Paginate a list of items.
    
    Args:
        items: List of items to paginate
        page: Page number (1-indexed)
        per_page: Items per page
    
    Returns:
        Dict with paginated data and metadata
    """
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    
    return {
        "items": items[start:end],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }
