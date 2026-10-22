from django.conf import settings
from django.core.files.storage import FileSystemStorage, Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class BlogMediaStorage(Storage):
    def __init__(self, resource_type='image'):
        self.resource_type = resource_type
        if settings.ENVIRONMENT == 'production':
            from cloudinary_storage.storage import MediaCloudinaryStorage, VideoMediaCloudinaryStorage

            storage_class = VideoMediaCloudinaryStorage if resource_type == 'video' else MediaCloudinaryStorage
            self._backend = storage_class()
        else:
            self._backend = FileSystemStorage(
                location=settings.MEDIA_ROOT,
                base_url=settings.MEDIA_URL,
            )

    def _open(self, name, mode='rb'):
        return self._backend._open(name, mode)

    def _save(self, name, content):
        return self._backend._save(name, content)

    def delete(self, name):
        return self._backend.delete(name)

    def exists(self, name):
        return self._backend.exists(name)

    def listdir(self, path):
        return self._backend.listdir(path)

    def size(self, name):
        return self._backend.size(name)

    def url(self, name):
        return self._backend.url(name)

    def path(self, name):
        return self._backend.path(name)

    def get_accessed_time(self, name):
        return self._backend.get_accessed_time(name)

    def get_created_time(self, name):
        return self._backend.get_created_time(name)

    def get_modified_time(self, name):
        return self._backend.get_modified_time(name)

    def get_available_name(self, name, max_length=None):
        return self._backend.get_available_name(name, max_length)

    def generate_filename(self, filename):
        return self._backend.generate_filename(filename)