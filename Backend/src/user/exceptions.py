from rest_framework.exceptions import APIException
from rest_framework import status

class ValidationException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid input'
    default_code = 'invalid'

    def __init__(self, detail=None, status_code=None):
        if detail is not None:
            self.detail = {'error': detail}
        if status_code is not None:
            self.status_code = status_code

class BlockingException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'A blocking condition has been detected.'
    default_code = 'blocking_error'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        super().__init__(detail, code)

class RelationshipException(APIException):
	status_code = status.HTTP_400_BAD_REQUEST
	default_detail = 'A relationship error has been detected.'
	default_code = 'relationship_error'

	def __init__(self, detail=None, code=None):
		if detail is None:
			detail = self.default_detail
		super().__init__(detail, code)