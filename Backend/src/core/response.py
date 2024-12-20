from rest_framework.response import Response
from rest_framework import status

# All our responses be send using one of these functions
# Therfore we can ensure that all responses have the same structure and
# the frontend can rely on this structure
#
# The variabe message should be always send using gettext to ensure that the
# frontend can display the message in the correct language. e.g.:
# return success_response(_("Registration successful"))
# The gettext can't be merged into this function, because the translation
# then would not be fetched by 'python manage.py makemessages' and this could
# lead to missing translations
#
# details can be any additional information that should be send to the frontend
# e.g.:
#   response_data = {
#       "userId": user.id,
#       "username": user.username,
#   }
#   return success_response(_("Welcome on board {username}!").format(username=user.username), **response_data)
def success_response(message: str, status_code=status.HTTP_200_OK, **json_details):
    return Response(
        {
            "status": "success",
            "statusCode": status_code,
            "message": message,
            **json_details,
        },
        status=status_code
    )

def error_response(message: str, status_code=status.HTTP_400_BAD_REQUEST, **json_details):
    return Response(
        {
            "status": "error",
            "statusCode": status_code,
            "message": message,
            **json_details,
        },
        status=status_code
    )
