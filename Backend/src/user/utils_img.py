import os
import uuid
from PIL import Image, ImageEnhance, ImageOps
import numpy as np
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
from user.utils import change_avatar_in_db
from core.exceptions import BarelyAnException
from django.utils.translation import gettext as _
from user.constants import AVATAR_FRAME
from rest_framework import status

# This function opens an image file and returns a PIL Image object
def open_image(img):
    try:
        return Image.open(img)
    except FileNotFoundError as e:
        raise BarelyAnException(_('Avatar file not found'), status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        raise BarelyAnException(_('Error opening image'), str(e))

# This function resizes an image to fit the avatar frame
def resize_image(image, min_width=186, min_height=208):
    try:
        return image.resize((min_width, min_height), Image.LANCZOS)
    except Exception as e:
        raise BarelyAnException(_('Error resizing image'))

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
        raise BarelyAnException(_('Error applying vintage filter'))

# This function adds our frame to an image
def add_frame(image):
    # Try to convert the image to RGB mode
    try:
        image = image.convert("RGB")
    except Exception as e:
        raise BarelyAnException(_('Error converting image to RGB'))

    # Load the frame image
    try:
        frame_path = os.path.join(settings.MEDIA_ROOT, 'avatars/', AVATAR_FRAME)
        print(frame_path)
        frame = open_image(frame_path)
    except Exception as e:
        raise BarelyAnException(_('Error loading frame image'))

    # Ensure both images are in RGBA mode (required for transparency)
    try:
        frame = frame.convert("RGBA")
        image = image.convert("RGBA")
    except Exception as e:
        raise BarelyAnException(_('Error converting images to RGBA'))

    # Create a blank image the same size as the frame, with transparency
    try:
        positioned_image = Image.new("RGBA", frame.size)
        positioned_image.paste(image, (15, 19))  # Paste the avatar image at (15, 19)
    except Exception as e:
        raise BarelyAnException(_('Error creating positioned image'))

    # Combine the frame and positioned image, preserving transparency
    try:
        final_image = Image.alpha_composite(positioned_image, frame)
    except Exception as e:
        raise BarelyAnException(_('Error combining images'))

    # Return the final image
    return final_image

def generate_filename_and_save(image):
    try:
        file_name = f"{uuid.uuid4()}.png"
        file_path = os.path.join(settings.MEDIA_ROOT, 'avatars/', file_name)
        temp_file = ContentFile(b'')  # Create a temporary file object
        image.save(temp_file, format="PNG", quality=85)
        temp_file.seek(0)  # Move to the beginning of the file so it can be read
        default_storage.save(file_path, temp_file)
    except Exception as e:
        raise BarelyAnException(_('Error saving image'), str(e))
    return file_name

# This function processes an avatar image file and returns a response
def process_avatar(user, avatar_file):
    if not avatar_file.content_type.startswith('image'):
        raise BarelyAnException(_('File type not supported'))
    image = open_image(avatar_file)
    image = resize_image(image)
    image = apply_filter(image)
    image = add_frame(image)
    file_name = generate_filename_and_save(image)
    change_avatar_in_db(user, file_name)
    return {'success': 'Avatar uploaded successfully', 'avatar_url': file_name}