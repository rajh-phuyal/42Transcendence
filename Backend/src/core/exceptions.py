from rest_framework.exceptions import APIException
from django.utils.translation import gettext as _
from rest_framework import status

class BarelyAnException(APIException):
    def __init__(self, detail=None, status_code=status.HTTP_400_BAD_REQUEST):
        super().__init__(detail)
        self.detail = detail or _("An error occurred.")
        self.status_code = status_code

class NotAuthenticated(BarelyAnException):
    def __init__(self, detail=None, status_code=status.HTTP_401_UNAUTHORIZED):
        super().__init__(detail)
        self.detail = detail or _("Authentication credentials were not provided.")
        self.status_code = status_code
