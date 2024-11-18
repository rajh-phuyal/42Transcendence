from rest_framework.exceptions import APIException
from rest_framework import status
from app.exceptions import BarelyAnException
import gettext as _

class ValidationException(BarelyAnException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Validation failed")

    def __init__(self, detail=None, status_code=None):
        detail = detail or self.default_detail
        status_code = status_code or self.status_code
        super().__init__(detail, status_code)

class BlockingException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('A blocking condition has been detected.')

    def __init__(self, detail=None, status_code=None):
        detail = detail or self.default_detail
        status_code = status_code or self.status_code
        super().__init__(detail, status_code)

class RelationshipException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('A relationship error has been detected.')
    
    def __init__(self, detail=None, status_code=None):
        detail = detail or self.default_detail
        status_code = status_code or self.status_code
        super().__init__(detail, status_code)