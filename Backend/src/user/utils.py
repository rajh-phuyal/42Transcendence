from rest_framework.response import Response
from rest_framework import status

def get_and_validate_data(request, action, doer_name, target_name):

    doer = request.data.get(doer_name)
    if not doer:
        return None, Response({'error': f'Key --> "{doer_name}".    {doer_name} must be provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    target = request.data.get(target_name)
    if not target:
        return None, Response({'error': f'Key --> "{target_name}".    {target_name} must be provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    if doer == target:
        return None, Response({'error': f'"{action}" failed.    {doer_name} and {target_name} cannot be the same'}, status=status.HTTP_400_BAD_REQUEST)
    
    return doer, target