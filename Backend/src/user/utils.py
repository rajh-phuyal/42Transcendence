from rest_framework.response import Response
from rest_framework import status
from .exceptions import ValidationException

def get_and_validate_data(request, action, target_name):

    doer = request.user
    # We don't need to check if doer is there because the user must be authenticated to reach this point
    
    # We extract the target from the JSON data
    target = request.data.get(target_name)
    if not target:
        raise ValidationException(f'Key --> "{target_name}".    {target_name} must be provided')
    
    if doer.username == target:
        raise ValidationException(f'"{action}" failed.    {doer.username} and {target_name} cannot be the same')
    
    return doer, target
