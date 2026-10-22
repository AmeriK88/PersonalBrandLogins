from pathlib import Path

from django.core.exceptions import ValidationError


def _file_signature(value, allowed_extensions, signature_check, label):
    extension = Path(value.name).suffix.lower()
    if extension not in allowed_extensions:
        raise ValidationError(f'Unsupported {label} file extension.')

    file_object = value.file
    position = file_object.tell()
    try:
        header = file_object.read(16)
    finally:
        file_object.seek(position)

    if not signature_check(header):
        raise ValidationError(f'The uploaded file is not a supported {label} format.')


def validate_audio_upload(value):
    _file_signature(
        value,
        {'.mp3', '.m4a', '.wav', '.ogg', '.flac'},
        lambda header: (
            header.startswith(b'ID3')
            or (len(header) >= 2 and header[0] == 0xFF and header[1] & 0xE0 == 0xE0)
            or (header.startswith(b'RIFF') and header[8:12] == b'WAVE')
            or header.startswith(b'OggS')
            or header.startswith(b'fLaC')
            or (header[4:8] == b'ftyp')
        ),
        'audio',
    )


def validate_video_upload(value):
    _file_signature(
        value,
        {'.mp4', '.m4v', '.mov', '.webm'},
        lambda header: header[4:8] == b'ftyp' or header.startswith(b'\x1aE\xdf\xa3'),
        'video',
    )