from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError


def validate_no_gps_metadata(value):
    file_object = value.file
    position = file_object.tell()
    try:
        with Image.open(file_object) as image:
            exif = image.getexif()
            gps_info = exif.get_ifd(0x8825)
            if gps_info:
                raise ValidationError(
                    'Remove GPS location metadata before uploading this image.'
                )
    except (OSError, UnidentifiedImageError) as error:
        raise ValidationError('Upload a valid image file.') from error
    finally:
        file_object.seek(position)
