from io import BytesIO
from struct import pack

from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import RequestFactory, TestCase, override_settings
from django.urls import resolve, reverse
from PIL import Image

from .admin import FamilyPhotoInline, FamilyPageAdmin
from .models import FamilyPage, FamilyPhoto, FamilyImageUploadTo
from .validators import validate_no_gps_metadata


@override_settings(
    CANONICAL_HOST='',
    STORAGES={
        **settings.STORAGES,
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    },
)
class FamilyPageTests(TestCase):
    def create_page(self, **kwargs):
        return FamilyPage.objects.create(**kwargs)

    def get_overview(self):
        return self.client.get(reverse('family:overview'))

    def test_family_url_resolves_to_namespaced_overview(self):
        response = resolve(reverse('family:overview'))

        self.assertEqual(response.app_name, 'family')
        self.assertEqual(response.url_name, 'overview')
        self.assertEqual(reverse('family:overview'), '/family/')

    def test_missing_or_unpublished_page_returns_404(self):
        self.assertEqual(self.get_overview().status_code, 404)

        page = self.create_page(is_published=False)
        response = self.get_overview()

        self.assertEqual(response.status_code, 404)
        page.refresh_from_db()
        self.assertFalse(page.is_published)

    def test_published_page_displays_approved_content_and_navigation(self):
        self.create_page(
            title='Family First',
            subtitle='The foundation behind every season.',
            introduction='Love, responsibility, and presence.',
            family_reflection='A life beyond basketball.',
            is_published=True,
        )

        response = self.get_overview()

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<h1 class="family-title fade-up delay-2">Family First</h1>',
            html=True,
        )
        self.assertContains(response, 'The foundation behind every season.')
        self.assertContains(response, 'Love, responsibility, and presence.')
        self.assertContains(response, 'A life beyond basketball.')
        self.assertContains(response, 'href="/family/"')
        self.assertContains(response, 'class="nav-link active"')
        self.assertContains(response, '>FAMILY</span>', html=False)
        self.assertContains(response, '>Family</a>', html=False)

    def test_optional_content_and_images_are_omitted_when_missing(self):
        page = self.create_page(is_published=True)

        response = self.get_overview()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, page.title)
        self.assertNotContains(response, 'family-hero-image')
        self.assertNotContains(response, 'family-gallery')
        self.assertNotContains(response, 'family-quote')
        self.assertNotContains(response, 'family-subtitle')

    def test_gallery_only_renders_visible_images_in_stable_order(self):
        page = self.create_page(is_published=True)
        later = FamilyPhoto.objects.create(
            page=page,
            image='family/gallery/later.jpg',
            alt_text='A family gathering outdoors',
            sort_order=2,
        )
        hidden = FamilyPhoto.objects.create(
            page=page,
            image='family/gallery/hidden.jpg',
            alt_text='An unapproved family photo',
            sort_order=0,
            is_visible=False,
        )
        earlier = FamilyPhoto.objects.create(
            page=page,
            image='family/gallery/earlier.jpg',
            alt_text='A family moment at an event',
            caption='A day together',
            sort_order=1,
        )

        response = self.get_overview()
        html = response.content.decode()

        self.assertLess(html.index(earlier.image.url), html.index(later.image.url))
        self.assertContains(response, 'A family moment at an event')
        self.assertContains(response, 'A day together')
        self.assertContains(response, 'A family gathering outdoors')
        self.assertContains(response, 'loading="lazy"')
        self.assertNotContains(response, hidden.image.name)
        self.assertNotContains(response, hidden.alt_text)

    def test_singleton_database_constraint_rejects_another_page(self):
        self.create_page(title='Only Family Page')

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                FamilyPage.objects.create(id=2, title='Duplicate')

        self.assertEqual(FamilyPage.objects.count(), 1)
        self.assertEqual(FamilyPage.objects.get().title, 'Only Family Page')

    def test_database_enforces_unpublished_singleton_default(self):
        page = self.create_page()

        self.assertEqual(page.pk, 1)
        self.assertEqual(page.title, 'Family First')
        self.assertFalse(page.is_published)
        self.assertTrue(FamilyPage._meta.get_field('subtitle').blank)
        self.assertTrue(FamilyPage._meta.get_field('hero_image').blank)

    def test_admin_registration_and_gallery_inline(self):
        self.assertIsInstance(admin.site._registry[FamilyPage], FamilyPageAdmin)
        self.assertIn(FamilyPhotoInline, FamilyPageAdmin.inlines)
        self.assertIs(FamilyPhotoInline.model, FamilyPhoto)
        self.assertEqual(
            FamilyPhotoInline.fields,
            ('image', 'alt_text', 'caption', 'sort_order', 'is_visible'),
        )

        form = admin.site._registry[FamilyPage].get_form(
            RequestFactory().get('/admin/family/familypage/add/')
        )
        self.assertIn('title', form.base_fields)
        self.assertIn('is_published', form.base_fields)
        self.assertIn('hero_image', form.base_fields)

    def test_existing_application_routes_still_resolve(self):
        for route_name in (
            'core:home',
            'core:about',
            'career:overview',
            'highlights:gallery',
            'blog:list',
            'family:overview',
        ):
            with self.subTest(route_name=route_name):
                self.assertTrue(resolve(reverse(route_name)))

    def test_upload_names_do_not_include_private_original_filenames(self):
        upload_path = FamilyImageUploadTo('gallery')(
            None,
            'private-family-photo.jpg',
        )

        self.assertRegex(
            upload_path,
            r'^family/gallery/[0-9a-f]{32}\.jpg$',
        )

    def test_gps_metadata_is_rejected_and_file_pointer_is_restored(self):
        tiff = b'II' + pack('<H', 42) + pack('<I', 8)
        tiff += pack('<H', 1) + pack('<HHII', 0x8825, 4, 1, 26) + pack('<I', 0)
        tiff += pack('<H', 1) + pack('<HHI', 1, 2, 2) + b'N\0\0\0' + pack('<I', 0)
        image_data = BytesIO()
        Image.new('RGB', (2, 2)).save(
            image_data,
            format='JPEG',
            exif=b'Exif\0\0' + tiff,
        )
        upload = SimpleUploadedFile('photo.jpg', image_data.getvalue())

        with self.assertRaisesMessage(ValidationError, 'GPS location metadata'):
            validate_no_gps_metadata(upload)

        self.assertEqual(upload.tell(), 0)

    def test_image_without_gps_metadata_passes_validator(self):
        image_data = BytesIO()
        Image.new('RGB', (2, 2)).save(image_data, format='JPEG')
        upload = SimpleUploadedFile('photo.jpg', image_data.getvalue())

        validate_no_gps_metadata(upload)

    def test_hero_image_requires_alternative_text(self):
        page = FamilyPage(
            hero_image='family/hero/photo.jpg',
            hero_image_alt=' ',
        )

        with self.assertRaises(ValidationError) as error:
            page.clean()

        self.assertIn('hero_image_alt', error.exception.message_dict)

    def test_family_app_is_registered(self):
        self.assertEqual(apps.get_app_config('family').name, 'family')
