import io
import os
from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image
from types import SimpleNamespace
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError

from .models import Post, PostReelMedia
from .validators import validate_audio_upload, validate_video_upload

MP4 = b'\x00\x00\x00\x18ftypmp42' + b'\x00' * 64


def png_bytes():
    buffer = io.BytesIO()
    Image.new('RGB', (2, 2), 'red').save(buffer, 'PNG')
    return buffer.getvalue()


class FakeCloudinaryStorage(Storage):
    """Mimics cloudinary_storage: _save returns the public_id WITHOUT extension,
    and _open downloads the bytes back from the (fake) CDN. No network access."""

    blobs = {}

    def __init__(self, resource_type):
        self.resource_type = resource_type

    def _save(self, name, content):
        stem, _ext = os.path.splitext(name.replace('\\', '/'))
        public_id = f'{stem}_x{len(self.blobs)}'
        self.blobs[(self.resource_type, public_id)] = content.read()
        return public_id

    def _open(self, name, mode='rb'):
        return ContentFile(self.blobs[(self.resource_type, name)], name=name)

    def exists(self, name):
        return (self.resource_type, name) in self.blobs

    def get_available_name(self, name, max_length=None):
        return name

    def url(self, name):
        return f'https://res.cloudinary.com/demo/{self.resource_type}/upload/{name}'


@override_settings(
    ALLOWED_HOSTS=['testserver'],
    STORAGES={
        **settings.STORAGES,
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    },
)
class ReelEditRegressionTests(TestCase):
    def setUp(self):
        FakeCloudinaryStorage.blobs = {}
        image_storage = FakeCloudinaryStorage('image')
        video_storage = FakeCloudinaryStorage('video')
        patches = [
            mock.patch.object(PostReelMedia._meta.get_field('image'), 'storage', image_storage),
            mock.patch.object(PostReelMedia._meta.get_field('video'), 'storage', video_storage),
            mock.patch.object(Post._meta.get_field('narration_audio'), 'storage', video_storage),
        ]
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)

        user = get_user_model().objects.create_superuser('admin', 'a@example.com', 'pw')
        self.client.force_login(user)
        self.post = Post.objects.create(title='T', slug='t', category='mindset', content='c')

    def formset(self, rows, extra_total):
        data = {
            'title': 'T', 'slug': 't', 'category': 'mindset', 'content': 'c',
            'reel_title': '', 'reel_description': '', 'is_published': 'on',
            'reel_media-TOTAL_FORMS': str(len(rows) + extra_total),
            'reel_media-INITIAL_FORMS': str(len(rows)),
            'reel_media-MIN_NUM_FORMS': '0',
            'reel_media-MAX_NUM_FORMS': '1000',
        }
        for i, row in enumerate(rows):
            data[f'reel_media-{i}-id'] = str(row['id'])
            data[f'reel_media-{i}-post'] = str(self.post.pk)
            data[f'reel_media-{i}-order'] = str(row['order'])
            data[f'reel_media-{i}-media_type'] = row['media_type']
            data[f'reel_media-{i}-caption'] = ''
            data[f'reel_media-{i}-alt_text'] = ''
        return data

    def add_row(self, data, index, media_type, order):
        from django.core.files.uploadedfile import SimpleUploadedFile
        data[f'reel_media-{index}-id'] = ''
        data[f'reel_media-{index}-post'] = str(self.post.pk)
        data[f'reel_media-{index}-order'] = str(order)
        data[f'reel_media-{index}-media_type'] = media_type
        data[f'reel_media-{index}-caption'] = ''
        data[f'reel_media-{index}-alt_text'] = ''
        if media_type == 'image':
            data[f'reel_media-{index}-image'] = SimpleUploadedFile('a.png', png_bytes(), 'image/png')
        else:
            data[f'reel_media-{index}-video'] = SimpleUploadedFile('a.mp4', MP4, 'video/mp4')

    def url(self):
        return reverse('admin:blog_post_change', args=[self.post.pk])

    def test_adding_reel_item_keeps_existing_items_unchanged(self):
        # 1. create image + video items through the admin
        data = self.formset([], 2)
        self.add_row(data, 0, 'image', 0)
        self.add_row(data, 1, 'video', 1)
        response = self.client.post(self.url(), data)
        self.assertEqual(response.status_code, 302, getattr(response, 'context_data', None) and response.context_data['inline_admin_formsets'][0].formset.errors)

        before = list(PostReelMedia.objects.values_list('id', 'media_type', 'image', 'video'))
        self.assertEqual(len(before), 2)
        image_item = PostReelMedia.objects.get(media_type='image')
        video_item = PostReelMedia.objects.get(media_type='video')
        urls_before = (image_item.image.url, video_item.video.url)
        self.assertFalse(os.path.splitext(video_item.video.name)[1], 'Cloudinary public_id has no extension')

        # 2. reopen the change page
        self.assertEqual(self.client.get(self.url()).status_code, 200)

        # 3. add a third item, resubmitting the existing rows unchanged
        rows = [
            {'id': i.pk, 'order': i.order, 'media_type': i.media_type}
            for i in PostReelMedia.objects.order_by('order')
        ]
        data = self.formset(rows, 1)
        self.add_row(data, 2, 'video', 2)
        response = self.client.post(self.url(), data)
        errors = response.context_data['inline_admin_formsets'][0].formset.errors if response.status_code == 200 else None
        self.assertEqual(response.status_code, 302, errors)

        # 4. originals untouched, new item valid
        after = list(PostReelMedia.objects.filter(pk__in=[b[0] for b in before]).values_list('id', 'media_type', 'image', 'video'))
        self.assertEqual(before, after)
        image_item.refresh_from_db()
        video_item.refresh_from_db()
        self.assertEqual(urls_before, (image_item.image.url, video_item.video.url))
        new_item = PostReelMedia.objects.exclude(pk__in=[b[0] for b in before]).get()
        self.assertTrue(new_item.video.url.startswith('https://res.cloudinary.com/demo/video/upload/blog/reels/videos/'))

    def test_existing_extensionless_video_passes_model_validation(self):
        item = PostReelMedia.objects.create(
            post=self.post, media_type='video', video='blog/reels/videos/clip_abc123'
        )
        FakeCloudinaryStorage.blobs[('video', 'blog/reels/videos/clip_abc123')] = MP4
        item.full_clean()


class ExistingFileValidationTests(TestCase):
    def setUp(self):
        FakeCloudinaryStorage.blobs = {}
        self.post = Post.objects.create(title='T', slug='t2', category='mindset', content='c')

    def test_stored_extensionless_media_validates_without_download(self):
        item = PostReelMedia.objects.create(
            post=self.post, media_type='video', video='blog/reels/videos/clip_abc'
        )
        storage = mock.Mock()
        storage._open.side_effect = AssertionError('remote download attempted')
        with mock.patch.object(PostReelMedia._meta.get_field('video'), 'storage', storage):
            item = PostReelMedia.objects.get(pk=item.pk)
            validate_video_upload(item.video)
        storage._open.assert_not_called()

    def test_stored_narration_validates_without_download(self):
        Post.objects.filter(pk=self.post.pk).update(narration_audio='blog/narration/n_abc')
        post = Post.objects.get(pk=self.post.pk)
        storage = mock.Mock()
        storage._open.side_effect = AssertionError('remote download attempted')
        with mock.patch.object(Post._meta.get_field('narration_audio'), 'storage', storage):
            validate_audio_upload(post.narration_audio)
        storage._open.assert_not_called()

    def test_new_uploads_are_still_validated(self):
        bad = [
            (validate_video_upload, SimpleUploadedFile('a.avi', MP4)),
            (validate_video_upload, SimpleUploadedFile('a.mp4', b'not a video at all')),
            (validate_audio_upload, SimpleUploadedFile('a.txt', b'ID3' + b'\0' * 20)),
            (validate_audio_upload, SimpleUploadedFile('a.mp3', b'garbage garbage garbage')),
        ]
        for validator, upload in bad:
            with self.subTest(name=upload.name), self.assertRaises(ValidationError):
                validator(upload)

    def test_new_model_assignment_is_uncommitted_and_validated(self):
        item = PostReelMedia(post=self.post, media_type='video')
        item.video = SimpleUploadedFile('a.avi', MP4)
        with self.assertRaises(ValidationError):
            validate_video_upload(item.video)

    def test_fake_committed_attribute_cannot_bypass_validation(self):
        upload = SimpleUploadedFile('a.avi', b'junk')
        upload._committed = True
        with self.assertRaises(ValidationError):
            validate_video_upload(upload)
        fake = SimpleNamespace(name='x', _committed=True, file=io.BytesIO(b'junk'))
        with self.assertRaises(ValidationError):
            validate_video_upload(fake)

    def test_image_field_has_no_extra_validators(self):
        self.assertEqual(PostReelMedia._meta.get_field('image').validators, [])


@override_settings(
    ALLOWED_HOSTS=['testserver'],
    STORAGES={
        **settings.STORAGES,
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    },
)
class NarrationTemplateTests(TestCase):
    def audio_tag(self, response):
        import re
        return re.search(r'<audio id="about-narration"[^>]*>', response.content.decode()).group(0)

    def test_cloudinary_style_narration_uses_manual_playback(self):
        post = Post.objects.create(title='N', slug='n', category='mindset', content='c')
        Post.objects.filter(pk=post.pk).update(narration_audio='blog/narration/n_abc')
        with mock.patch.object(Post._meta.get_field('narration_audio'), 'storage', FakeCloudinaryStorage('video')):
            response = self.client.get(reverse('blog:detail', args=['n']))
        tag = self.audio_tag(response)
        self.assertNotIn('autoplay', tag)
        self.assertNotIn('muted', tag)
        self.assertIn('preload="none"', tag)
        self.assertContains(response, 'https://res.cloudinary.com/demo/video/upload/blog/narration/n_abc')
        self.assertContains(response, 'aria-pressed="false"')

    def test_legacy_narration_fallback_uses_manual_playback(self):
        Post.objects.create(title='L', slug='watch-this-the-story-of-my-comeback', category='mindset', content='c')
        response = self.client.get(reverse('blog:detail', args=['watch-this-the-story-of-my-comeback']))
        tag = self.audio_tag(response)
        self.assertNotIn('autoplay', tag)
        self.assertNotIn('muted', tag)
        self.assertContains(response, 'static/audio/narration.mp3')
