from rest_framework import status
from core.exceptions import BarelyAnException
from django.utils.translation import gettext as _

class ValidationException(BarelyAnException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Validation failed")

    def __init__(self, detail=None, status_code=None):
        detail = detail or self.default_detail
        status_code = status_code or self.status_code
        super().__init__(detail, status_code)

class UserNotFound(BarelyAnException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('User not found')

    def __init__(self, detail=None, status_code=None):
        detail = detail or self.default_detail
        status_code = status_code or self.status_code
        super().__init__(detail, status_code)

class BlockingException(BarelyAnException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('A blocking condition has been detected.')

    def __init__(self, detail=None, status_code=None):
        detail = detail or self.default_detail
        status_code = status_code or self.status_code
        super().__init__(detail, status_code)

class RelationshipException(BarelyAnException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('A relationship error has been detected.')

    def __init__(self, detail=None, status_code=None):
        detail = detail or self.default_detail
        status_code = status_code or self.status_code
        super().__init__(detail, status_code)