from rest_framework.exceptions import APIException
from django.utils.translation import gettext as _
from rest_framework import status

class BarelyAnException(APIException):
    def __init__(self, detail, status_code=status.HTTP_400_BAD_REQUEST):
        super().__init__(detail)		# Allows APIException to handle `detail` first
        self.detail = detail            # Ensures our custom `self.detail` is explicitly set
        self.status_code = status_code

class NotAuthenticated(BarelyAnException):
    status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(self, detail, status_code=status.HTTP_401_UNAUTHORIZED):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail or _("Authentication credentials were not provided.")
