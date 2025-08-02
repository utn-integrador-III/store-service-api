from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional
from enum import Enum
from . import message_codes 

class StatusCode(Enum):
    
    # Successful Status codes
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    
    # Client Error Status Codes
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    
    # Server Error Status Codes
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503

def create_response(
    status_code: StatusCode,
    data: Optional[Any] = None,
    message: Optional[str] = None,
    message_code: Optional[str] = None,
) -> JSONResponse:
    """
    Creates a standardized JSON response, automatically setting default
    messages based on the status code if not provided.
    
    Args:
        status_code (StatusCode): The HTTP status code for the response.
        data (Optional[Any]): The data to be included in the response. Defaults to None.
        message (Optional[str]): A custom message for the response. Defaults to None.
        message_code (Optional[str]): A custom message code. Defaults to None.
        
    Returns:
        JSONResponse: A FastAPI JSON response object.
    """
    
    # Default messages and codes based on status
    if message is None:
        default_messages = {
            StatusCode.OK: ("Success", message_codes.SUCCESS),
            StatusCode.CREATED: ("Resource created successfully", message_codes.CREATED),
            StatusCode.NOT_FOUND: ("Resource not found", message_codes.NOT_FOUND),
            StatusCode.BAD_REQUEST: ("Bad Request", message_codes.BAD_REQUEST),
            StatusCode.UNAUTHORIZED: ("Unauthorized", message_codes.UNAUTHORIZED),
            StatusCode.CONFLICT: ("Conflict with current state of the resource", message_codes.CONFLICT),
            StatusCode.INTERNAL_SERVER_ERROR: ("An internal server error occurred", message_codes.INTERNAL_SERVER_ERROR),
        }
        message, default_code = default_messages.get(status_code, ("An error occurred", "ERROR"))
        if message_code is None:
            message_code = default_code

    response_content: Dict[str, Any] = {
        "data": data,
        "message": message,
        "message_code": message_code,
    }
    
    return JSONResponse(content=response_content, status_code=status_code.value)

# Success Responses
def success_response(data: Optional[Any] = None) -> JSONResponse:
    return create_response(status_code=StatusCode.OK, data=data)

def created_response(data: Optional[Any] = None) -> JSONResponse:
    return create_response(status_code=StatusCode.CREATED, data=data)

# Error Responses
def bad_request_response(message: str = "Bad Request", message_code: str = message_codes.BAD_REQUEST) -> JSONResponse:
    return create_response(status_code=StatusCode.BAD_REQUEST, message=message, message_code=message_code)

def not_found_response() -> JSONResponse:
    return create_response(status_code=StatusCode.NOT_FOUND)

def unauthorized_response() -> JSONResponse:
    return create_response(status_code=StatusCode.UNAUTHORIZED)
    
def conflict_response() -> JSONResponse:
    return create_response(status_code=StatusCode.CONFLICT)

def internal_server_error_response() -> JSONResponse:
    return create_response(status_code=StatusCode.INTERNAL_SERVER_ERROR)