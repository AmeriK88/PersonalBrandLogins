from django.test import TestCase
from django.test import override_settings
from django.urls import reverse

from .models import Highlight


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class HighlightsGalleryTests(TestCase):
    def get_gallery(self):
        return self.client.get(reverse("highlights:gallery"))

    def test_gallery_renders_all_existing_categories_and_safe_video_embed(self):
        photo = Highlight.objects.create(
            title="Game night",
            category="photo",
            description="A moment from the game.",
            image="highlights/game-night.jpg",
            video_url="https://youtu.be/abcdefghijk",
            press_link="https://example.com/story",
        )
        video = Highlight.objects.create(
            title="Court action",
            category="video",
            image="highlights/court-action.jpg",
            video_url="https://www.youtube.com/watch?v=123456789ab",
        )
        press = Highlight.objects.create(
            title="The interview",
            category="press",
            description="A conversation about the game.",
            image="highlights/interview.jpg",
            press_link="https://example.com/interview",
        )

        response = self.get_gallery()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Through the Lens")
        self.assertContains(response, "Game Film")
        self.assertContains(response, "Beyond the Game")
        self.assertContains(
            response,
            'data-video-embed="https://www.youtube-nocookie.com/embed/123456789ab"',
        )
        self.assertContains(response, 'href="https://example.com/story"')
        self.assertContains(response, 'href="https://example.com/interview"')
        self.assertEqual(list(response.context["photos"]), [photo])
        self.assertEqual(list(response.context["videos"]), [video])
        self.assertEqual(list(response.context["press"]), [press])

    def test_empty_gallery_renders_editorial_empty_state(self):
        response = self.get_gallery()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The archive is taking shape.")
        self.assertContains(response, "THE JOURNEY CONTINUES.")
        self.assertNotContains(response, "Through the Lens")
        self.assertNotContains(response, "Game Film")
        self.assertNotContains(response, "Beyond the Game")

    def test_missing_images_do_not_break_gallery_or_create_hero_image(self):
        Highlight.objects.create(title="Photo without image", category="photo")
        Highlight.objects.create(title="Video without poster", category="video")

        response = self.get_gallery()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Photo without image")
        self.assertContains(response, "Video without poster")
        self.assertEqual(response.context["hero_image"], "")
        self.assertNotContains(response, "archive-hero-image")

    def test_video_image_is_preferred_for_hero(self):
        Highlight.objects.create(
            title="Photo poster",
            category="photo",
            image="highlights/photo.jpg",
        )
        Highlight.objects.create(
            title="Video poster",
            category="video",
            image="highlights/video.jpg",
        )

        response = self.get_gallery()

        self.assertContains(response, "archive-hero-image")
        self.assertEqual(
            response.context["hero_image"],
            "/media/highlights/video.jpg",
        )

    def test_photo_image_is_used_as_hero_fallback(self):
        Highlight.objects.create(
            title="Photo poster",
            category="photo",
            image="highlights/photo.jpg",
        )
        Highlight.objects.create(title="Video without poster", category="video")

        response = self.get_gallery()

        self.assertEqual(
            response.context["hero_image"],
            "/media/highlights/photo.jpg",
        )

    def test_unsupported_video_host_never_becomes_an_iframe_source(self):
        Highlight.objects.create(
            title="Unsupported source",
            category="video",
            video_url="https://attacker.example/watch/abcdefghijk",
        )

        response = self.get_gallery()

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "data-video-embed")
        self.assertContains(
            response,
            'href="https://attacker.example/watch/abcdefghijk"',
        )

    def test_vimeo_video_and_unlisted_hash_are_supported(self):
        Highlight.objects.create(
            title="Public Vimeo",
            category="video",
            video_url="https://vimeo.com/123456789",
        )
        Highlight.objects.create(
            title="Unlisted Vimeo",
            category="video",
            video_url="https://vimeo.com/987654321/abc123",
        )

        response = self.get_gallery()

        self.assertContains(
            response,
            'data-video-embed="https://player.vimeo.com/video/123456789"',
        )
        self.assertContains(
            response,
            'data-video-embed="https://player.vimeo.com/video/987654321?h=abc123"',
        )

    def test_unsafe_external_links_are_not_rendered(self):
        Highlight.objects.create(
            title="Unsafe links",
            category="press",
            video_url="javascript:alert(1)",
            press_link="javascript:alert(2)",
        )

        response = self.get_gallery()

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "javascript:")
        self.assertNotContains(response, "data-video-embed")
