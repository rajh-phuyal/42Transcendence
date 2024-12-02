from functools import wraps
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from core.exceptions import BarelyAnException
from core.response import error_response
from django.utils.translation import gettext as _
import logging

# This decorator is used to catch exceptions and return a generic error response
# we should use it for all http requests like post, get, put, delete
def barely_handle_exceptions(view_func):
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        try:
            return view_func(self, request, *args, **kwargs)
        except BarelyAnException as e:
            return error_response(str(e.detail), e.status_code)
        except ObjectDoesNotExist as e:
            model_name = getattr(e, 'model', None)
            model_name = model_name.__name__ if model_name else _("Object")
            return error_response(_("{model_name} entry not found").format(model_name=model_name), status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # For unexpected exceptions, fallback to a generic error response
            return error_response(_("An unexpected error occurred: {error}").format(error=str(e)))
    return wrapper

def barely_handle_ws_exceptions(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except BarelyAnException as e:
            logging.info(f"BarelyAnException occurred: {str(e.detail)} | Status code: {e.status_code}")
        except ObjectDoesNotExist as e:
            model_name = getattr(e, 'model', None)
            model_name = model_name.__name__ if model_name else _("Object")
            logging.info(f"{model_name} entry not found: {str(e)}")
        except Exception as e:
            # For unexpected exceptions, fallback to a generic error response
            logging.info(f"Unexpected error occurred in WebSocket: {str(e)}")
    return wrapper