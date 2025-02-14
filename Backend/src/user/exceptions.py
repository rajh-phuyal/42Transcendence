from rest_framework import status
from core.exceptions import BarelyAnException
from django.utils.translation import gettext as _

class ValidationException(BarelyAnException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail=None, status_code=None):
        super().__init__(detail, status_code)
        self.detail = detail or _("Validation failed")
        self.status_code = status_code or self.status_code

class UserNotFound(BarelyAnException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail=None, status_code=None):
        super().__init__(detail, status_code)
        self.detail = detail or _('User not found')
        self.status_code = status_code or self.status_code

class BlockingException(BarelyAnException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail=None, status_code=None):
        super().__init__(detail, status_code)
        self.detail = detail or _('A blocking condition has been detected.')
        self.status_code = status_code or self.status_code

class RelationshipException(BarelyAnException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail=None, status_code=None):
        super().__init__(detail, status_code)
        self.detail = detail or _('A relationship error has been detected.')
        self.status_code = status_code or self.status_code