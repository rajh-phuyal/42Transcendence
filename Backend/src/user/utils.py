from rest_framework.response import Response
from rest_framework import status
from .exceptions import ValidationException

def get_and_validate_data(request, action, doer_name, target_name):

    doer = request.data.get(doer_name)
    if not doer:
        raise ValidationException(f'Key --> "{doer_name}".    {doer_name} must be provided')
    
    target = request.data.get(target_name)
    if not target:
        raise ValidationException(f'Key --> "{target_name}".    {target_name} must be provided')
    
    if doer == target:
        raise ValidationException(f'"{action}" failed.    {doer_name} and {target_name} cannot be the same')
    
    return doer, target
