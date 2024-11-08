import os
import uuid
from PIL import Image, ImageEnhance, ImageOps
import numpy as np
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
from rest_framework.response import Response
from .models import NoCoolWith
from .exceptions import ValidationException, BlockingException

def get_and_validate_data(request, action, target_name):

    doer = request.user
    # We don't need to check if doer is there because the user must be authenticated to reach this point
    
    # We extract the target from the JSON data
    target = request.data.get(target_name)
    if not target:
        raise ValidationException(f'Key --> "{target_name}".    {target_name} must be provided')

    # Check if the target is in a user table
    if not doer.__class__.objects.filter(id=target).exists():
        raise ValidationException(f'{target_name} not found')

    if doer.id == target:
        if action == 'remove':
            action = 'remov'

        raise ValidationException(f'{action}ing failed.  Cannot do it to yourself')
    
    return doer, target

def check_blocking(requestee_id, requester_id):
    # Check if the requestee has blocked the requester
    requestee_blocked = NoCoolWith.objects.filter(blocker_id=requestee_id, blocked_id=requester_id)
    if requestee_blocked.exists():
        raise BlockingException(detail='You have been blocked by this user.')

    # Check if the requester has blocked the requestee
    requester_blocked = NoCoolWith.objects.filter(blocker_id=requester_id, blocked_id=requestee_id)
    if requester_blocked.exists():
        raise BlockingException(detail='You have blocked this user, you need to unblock them first.')

def process_avatar(user, avatar_file):
    if not avatar_file.content_type.startswith('image'):
        return {'error': 'File type not supported'}

    try:
        # Try to open the image
        try:
            image = Image.open(avatar_file)
        except FileNotFoundError as e:
            return {'error': 'Avatar file not found', 'details': str(e)}
        except IOError as e:
            return {'error': 'Error opening image file', 'details': str(e)}
        except Exception as e:
            return {'error': 'Unexpected error opening image', 'details': str(e)}

		# Apply a sepia filter and some noise for an old-fashioned look
        try:
            # Convert the image to grayscale first
            image = ImageOps.grayscale(image)

            # Enhance contrast to make it look more aged
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)

            # Apply sepia tone by blending with an orange color
            sepia = Image.new("RGB", image.size, (112, 66, 20))  # Sepia color
            image = Image.blend(image.convert("RGB"), sepia, 0.3)

            # Add some noise for a grainy effect
            noise = np.random.normal(0, 25, (image.height, image.width, 3))
            noise_image = np.array(image) + noise
            noise_image = np.clip(noise_image, 0, 255).astype("uint8")
            image = Image.fromarray(noise_image)
        except Exception as e:
            return {'error': 'Error applying vintage filter', 'details': str(e)}
        
        # Try to convert the image to RGB mode
        try:
            image = image.convert("RGB")
        except Exception as e:
            return {'error': 'Error converting image to RGB', 'details': str(e)}

        # Try to resize the image while maintaining aspect ratio
        max_size = 512
        try:
            image.thumbnail((max_size, max_size), Image.LANCZOS)
        except Exception as e:
            return {'error': 'Error resizing image', 'details': str(e)}

        # Try to generate a unique filename
        try:
            file_name = f"{uuid.uuid4()}.jpg"
            file_path = os.path.join(settings.MEDIA_ROOT, 'avatars/', file_name)
        except Exception as e:
            return {'error': 'Error generating unique filename', 'details': str(e)}

        # Try to save the image with compression
        try:
            temp_file = ContentFile(b'')  # Create a temporary file object
            try:
                image.save(temp_file, format="JPEG", quality=85)  # Adjust quality for compression
            except IOError as e:
                return {'error': 'Error saving image with compression', 'details': str(e)}
            temp_file.seek(0)  # Move to the beginning of the file so it can be read
        except Exception as e:
            return {'error': 'Error creating temporary file or setting up compression', 'details': str(e)}

        # Try to save the file to default storage
        try:
            default_storage.save(file_path, temp_file)
        except Exception as e:
            return {'error': 'Error saving image to storage', 'details': str(e)}

    except Exception as e:
        return {'error': 'Unexpected error during image processing', 'details': str(e)}

    # Update user's avatar_path field and save the user model
    user.avatar_path = file_name
    user.save()

    # Return the avatar URL
    return {'success': 'Avatar uploaded successfully', 'avatar_url': file_path}