import os
import uuid
from PIL import Image, ImageEnhance, ImageOps
import numpy as np
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
from .utils import change_avatar
from rest_framework.response import Response
from app.exceptions import BarelyAnException
import gettext as _

# This function opens an image file and returns a PIL Image object
def open_image(img):
    try:
        return Image.open(img)
    except FileNotFoundError as e:
        return {'error': 'Avatar file not found', 'details': str(e)}
    except IOError as e:
        return {'error': 'Error opening image file', 'details': str(e)}
    except Exception as e:
        return {'error': 'Unexpected error opening image', 'details': str(e)}

# This function resizes an image to fit the avatar frame
def resize_image(image, min_width=186, min_height=208):
    try:
        return image.resize((min_width, min_height), Image.LANCZOS)
    except Exception as e:
        raise RuntimeError(f"Error resizing image: {str(e)}")

# This function applies a vintage filter to an image, giving it an aged look
def apply_filter(image):
    try:
        # Convert the image to grayscale firs
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

        # Return the processed image
        return image
    except Exception as e:
        raise RuntimeError(f"Error applying filter: {str(e)}")

# This function adds our frame to an image
def add_frame(image):
    # Try to convert the image to RGB mode
    try:
        image = image.convert("RGB")
    except Exception as e:
        return {'error': 'Error converting image to RGB', 'details': str(e)}

    # Load the frame image
    try:
        frame_path = os.path.join(settings.MEDIA_ROOT, 'avatars/avatar_frame.png')
        frame = open_image(frame_path)
    except Exception as e:
        return {'error': 'Error opening frame image file', 'details': str(e)}

    # Ensure both images are in RGBA mode (required for transparency)
    try:
        frame = frame.convert("RGBA")
        image = image.convert("RGBA")
    except Exception as e:
        return {'error': 'Error converting frame or image to RGBA', 'details': str(e)}

    # Create a blank image the same size as the frame, with transparency
    try:
        positioned_image = Image.new("RGBA", frame.size)
        positioned_image.paste(image, (15, 19))  # Paste the avatar image at (15, 19)
    except Exception as e:
        return {'error': 'Error creating blank image or pasting avatar', 'details': str(e)}
    
    # Combine the frame and positioned image, preserving transparency
    try:
        final_image = Image.alpha_composite(positioned_image, frame)
    except Exception as e:
        return {'error': 'Error combining frame and image', 'details': str(e)}

    # Return the final image
    return final_image

# This function processes an avatar image file and returns a response    
def process_avatar(user, avatar_file):
    if not avatar_file.content_type.startswith('image'):
        raise BarelyAnException(_('File type not supported'))

    # Try to open the image
    try:
        image = open_image(avatar_file)
    except Exception as e:
        raise BarelyAnException(_('Error opening image'), details=str(e))

    # Resize the image to fit the avatar frame
    try:
        image = resize_image(image)
    except Exception as e:
        raise BarelyAnException(_('Error resizing image'), details=str(e))

    # Apply a sepia filter and some noise for an old-fashioned look
    try:
        image = apply_filter(image)
    except Exception as e:
        raise BarelyAnException(_('Error applying vintage filter'), details=str(e))
    
    # Add the frame to the image
    try:
        image = add_frame(image)
    except Exception as e:
        raise BarelyAnException(_('Error adding frame to image'), details=str(e))

    # Try gerneating unique filename and to save the image with compression
    try:
        file_name = f"{uuid.uuid4()}.png"
        file_path = os.path.join(settings.MEDIA_ROOT, 'avatars/', file_name)
        temp_file = ContentFile(b'')  # Create a temporary file object
        image.save(temp_file, format="PNG", quality=85)
        temp_file.seek(0)  # Move to the beginning of the file so it can be read
        default_storage.save(file_path, temp_file)
    except Exception as e:
        raise BarelyAnException(_('Error saving image'), details=str(e))

    # Update the user's avatar in the database
    change_avatar(user, file_name)

    # Return the avatar URL
    return {'success': 'Avatar uploaded successfully', 'avatar_url': file_name}