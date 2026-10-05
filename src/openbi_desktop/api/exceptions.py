"""Exceptions raised by the OpenBI API client."""


class OpenBIError(Exception):
    """Base class for all OpenBI client errors."""


class ConnectionError_(OpenBIError):
    """Could not reach the OpenBI backend."""


class APIError(OpenBIError):
    """Backend returned a non-success HTTP status."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"HTTP {status_code}: {message}")


class ParseError(OpenBIError):
    """Backend returned a response we could not parse."""
