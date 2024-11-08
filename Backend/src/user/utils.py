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

def resize_and_crop(image, min_width=186, min_height=208):
    """
    Resizes an image to meet minimum width and height requirements, maintaining aspect ratio,
    and then center-crops to the exact dimensions.
    
    :param image: PIL Image object to resize and crop
    :param min_width: Minimum width of the resulting image
    :param min_height: Minimum height of the resulting image
    :return: Resized and cropped PIL Image object
    """
    try:
        # Get the current dimensions and aspect ratio
        width, height = image.size
        aspect_ratio = width / height

        # Calculate new dimensions to meet minimum width and height while preserving aspect ratio
        if width < min_width or height < min_height:
            if aspect_ratio > 1:  # Wider than tall
                new_width = max(min_width, int(height * aspect_ratio))
                new_height = max(min_height, int(new_width / aspect_ratio))
            else:  # Taller than wide or square
                new_height = max(min_height, int(width / aspect_ratio))
                new_width = max(min_width, int(new_height * aspect_ratio))
        else:
            new_width = max(min_width, width)
            new_height = max(min_height, height)

        # Resize the image
        image = image.resize((new_width, new_height), Image.LANCZOS)

        # Center-crop to the exact target size
        left = (new_width - min_width) / 2
        top = (new_height - min_height) / 2
        right = (new_width + min_width) / 2
        bottom = (new_height + min_height) / 2
        image = image.crop((left, top, right, bottom))

        return image

    except Exception as e:
        raise RuntimeError(f"Error resizing or cropping image: {str(e)}")

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

        # Resize and crop the image to fit the avatar frame
        try:
            image = resize_and_crop(image)
        except Exception as e:
            return {'error': 'Error resizing and cropping image', 'details': str(e)}
            
        # Load the frame image
        try:
            frame_path = os.path.join(settings.MEDIA_ROOT, 'avatars/avatar_frame.png')
            frame = Image.open(frame_path)
        except FileNotFoundError as e:
            return {'error': 'Frame file not found', 'details': str(e)}
        except IOError as e:
            return {'error': 'Error opening frame image file', 'details': str(e)}

        # Ensure frame has an alpha channel
        frame = frame.convert("RGBA")
        
        # Ensure the avatar image is also in RGBA mode (required for transparency)
        image = image.convert("RGBA")
        
        # Create a blank image the same size as the frame, with transparency
        positioned_image = Image.new("RGBA", frame.size)
        positioned_image.paste(image, (15, 19))  # Paste the avatar image at (15, 19)
        
        # Combine the frame and positioned image, preserving transparency
        final_image = Image.alpha_composite(positioned_image, frame)

        # Paste the avatar onto the frame at the specified coordinates
        #frame.paste(image, (15, 19))

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
                final_image.save(temp_file, format="PNG", quality=85)  # Adjust quality for compression
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

    # Check if there's an existing avatar and delete it if it's not the default
    if user.avatar_path and user.avatar_path != "default_avatar.png":
        old_avatar_path = os.path.join(settings.MEDIA_ROOT, 'avatars/', user.avatar_path)
        if default_storage.exists(old_avatar_path):
            default_storage.delete(old_avatar_path)
    
    # Update user's avatar_path field and save the user model
    user.avatar_path = file_name
    user.save()

    # Return the avatar URL
    return {'success': 'Avatar uploaded successfully', 'avatar_url': file_path}