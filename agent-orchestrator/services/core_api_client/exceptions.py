"""Custom exceptions for CoreApiClient"""


class CoreApiException(Exception):
    """Base exception for CoreApi client"""


class CoreApiHttpException(CoreApiException):
    """HTTP-related exceptions"""

    def __init__(self, message: str, status_code: int = None, response_text: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class CoreApiNotFound(CoreApiHttpException):
    """Resource not found (404)"""


class CoreApiUnauthorized(CoreApiHttpException):
    """Unauthorized access (401)"""


class CoreApiForbidden(CoreApiHttpException):
    """Forbidden access (403)"""


class CoreApiServerError(CoreApiHttpException):
    """Server error (5xx)"""


class CoreApiConnectionError(CoreApiException):
    """Connection-related errors"""


class CoreApiTimeout(CoreApiException):
    """Request timeout"""


class CoreApiValidationError(CoreApiException):
    """Validation error for request/response data"""
