from rest_framework import status
from core.exceptions import BarelyAnException
from django.utils.translation import gettext as _

class ValidationException(BarelyAnException):
    def __init__(self, detail=None, status_code=status.HTTP_400_BAD_REQUEST):
        super().__init__(detail, status_code)
        self.detail = detail or _("Validation failed")
        self.status_code = status_code

class UserNotFound(BarelyAnException):
    def __init__(self, detail=None, status_code=status.HTTP_404_NOT_FOUND):
        super().__init__(detail, status_code)
        self.detail = detail or _('User not found')
        self.status_code = status_code

class BlockingException(BarelyAnException):
    def __init__(self, detail=None, status_code=status.HTTP_400_BAD_REQUEST):
        super().__init__(detail, status_code)
        self.detail = detail or _('A blocking condition has been detected.')
        self.status_code = status_code

class RelationshipException(BarelyAnException):
    def __init__(self, detail=None, status_code=status.HTTP_400_BAD_REQUEST):
        super().__init__(detail, status_code)
        self.detail = detail or _('A relationship error has been detected.')
        self.status_code = status_code