from rest_framework.exceptions import APIException
from django.utils.translation import gettext as _

class BarelyAnException(APIException):
    def __init__(self, detail, status_code=400):
        super().__init__(detail)		# Allows APIException to handle `detail` first
        self.detail = detail			# Ensures our custom `self.detail` is explicitly set
        self.status_code = status_code

class NotAuthenticated(BarelyAnException):
    status_code = 401
    default_detail = _("Authentication credentials were not provided.")

    def __init__(self, detail, status_code=401):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = {
            "status": "error",
            "statusCode": self.status_code,
            "message": detail
        }