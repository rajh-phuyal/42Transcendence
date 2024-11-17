from rest_framework.response import Response
from rest_framework import status

def success_response(message: str, details=None, status_code=status.HTTP_200_OK):
    return Response(
        {
            "status": "success",
            "message": message,
            "details": details,
        },
        status=status_code
    )

def error_response(message: str, details=None, status_code=status.HTTP_400_BAD_REQUEST):
    return Response(
        {
            "status": "error",
            "message": message,
            "details": details,
        },
        status=status_code
    )
