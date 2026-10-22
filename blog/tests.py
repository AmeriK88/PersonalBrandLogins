from importlib import import_module
from types import SimpleNamespace

from django.contrib import admin
from django.apps import apps
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.db import connection
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from .admin import PostReelMediaInline
from .models import Post, PostReelMedia
from .validators import validate_audio_upload, validate_video_upload


@override_settings(
	CANONICAL_HOST='',
	STORAGES={
		**settings.STORAGES,
		'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
	},
)
class BlogMultimediaTests(TestCase):
	def make_post(self, title, slug):
		return Post.objects.create(
			title=title,
			slug=slug,
			category='mindset',
			content='Article text',
		)

	def detail(self, post):
		return self.client.get(reverse('blog:detail', args=[post.slug]))

	def test_posts_without_multimedia_render_without_empty_components(self):
		post = self.make_post('No media', 'no-media')

		response = self.detail(post)

		self.assertEqual(response.status_code, 200)
		self.assertNotContains(response, 'id="about-narration"')
		self.assertNotContains(response, 'id="about-audio-toggle"')
		self.assertNotContains(response, 'id="recovery-reel"')

	def test_audio_without_reel_renders_only_narration_controls(self):
		post = self.make_post('Audio only', 'audio-only')
		post.narration_audio = 'blog/narration/story.mp3'
		post.save()

		response = self.detail(post)

		self.assertContains(response, 'id="about-narration"')
		self.assertContains(response, 'id="about-audio-toggle"')
		self.assertNotContains(response, 'id="recovery-reel"')

	def test_reel_without_audio_renders_without_audio_controls(self):
		post = self.make_post('Reel only', 'reel-only')
		PostReelMedia.objects.create(
			post=post,
			media_type=PostReelMedia.IMAGE,
			image='blog/reels/images/story.webp',
		)

		response = self.detail(post)

		self.assertContains(response, 'id="recovery-reel"')
		self.assertNotContains(response, 'id="about-narration"')
		self.assertNotContains(response, 'id="about-audio-toggle"')

	def test_reel_metadata_fields_are_optional_and_exposed_in_admin(self):
		for field_name in ('reel_title', 'reel_description'):
			field = Post._meta.get_field(field_name)
			self.assertTrue(field.blank)
			self.assertFalse(field.null)

		post_admin = admin.site._registry[Post]
		form = post_admin.get_form(RequestFactory().get('/admin/blog/post/add/'))
		self.assertIn('reel_title', form.base_fields)
		self.assertIn('reel_description', form.base_fields)
		self.assertFalse(form.base_fields['reel_title'].required)
		self.assertFalse(form.base_fields['reel_description'].required)
		self.assertIn(PostReelMediaInline, post_admin.inlines)

	def test_custom_reel_metadata_is_displayed_for_each_post(self):
		post = self.make_post('Custom reel', 'custom-reel')
		post.reel_title = 'Training Highlights'
		post.reel_description = 'A look at this article’s key moments.'
		post.save()
		PostReelMedia.objects.create(
			post=post,
			media_type=PostReelMedia.IMAGE,
			image='blog/reels/images/training.webp',
		)

		response = self.detail(post)

		self.assertContains(response, 'Training Highlights')
		self.assertContains(response, 'A look at this article’s key moments.')
		self.assertNotContains(response, 'Recovery Reel')

	def test_reel_without_metadata_uses_neutral_title_and_omits_empty_description(self):
		post = self.make_post('Unconfigured reel', 'unconfigured-reel')
		PostReelMedia.objects.create(
			post=post,
			media_type=PostReelMedia.IMAGE,
			image='blog/reels/images/unconfigured.webp',
		)

		response = self.detail(post)
		html = response.content.decode()

		self.assertContains(response, 'Media Reel')
		self.assertNotRegex(
			html,
			r'<p[^>]*class="small text-secondary mb-3 fade-in"[^>]*>\s*</p>',
		)

	def test_post_narration_and_reel_render_from_owned_media(self):
		post = self.make_post('Has media', 'has-media')
		post.narration_audio = 'blog/narration/story.mp3'
		post.save()
		PostReelMedia.objects.create(
			post=post,
			media_type=PostReelMedia.IMAGE,
			image='blog/reels/images/story.webp',
			alt_text='<script>alert(1)</script>',
		)

		response = self.detail(post)

		self.assertContains(response, 'id="about-narration"')
		self.assertContains(response, 'id="recovery-reel"')
		self.assertContains(response, 'src="/media/blog/reels/images/story.webp"')
		self.assertContains(response, 'alt="&lt;script&gt;alert(1)&lt;/script&gt;"')
		self.assertNotContains(response, 'static/audio/narration.mp3')

	def test_reel_order_and_post_isolation(self):
		first_post = self.make_post('First', 'first')
		second_post = self.make_post('Second', 'second')
		later = PostReelMedia.objects.create(
			post=first_post,
			media_type=PostReelMedia.IMAGE,
			image='blog/reels/images/later.webp',
			order=2,
		)
		earlier = PostReelMedia.objects.create(
			post=first_post,
			media_type=PostReelMedia.VIDEO,
			video='blog/reels/videos/earlier.mp4',
			order=1,
		)
		PostReelMedia.objects.create(
			post=second_post,
			media_type=PostReelMedia.IMAGE,
			image='blog/reels/images/other.webp',
		)

		self.assertEqual(list(first_post.reel_media.all()), [earlier, later])
		first_response = self.detail(first_post)
		second_response = self.detail(second_post)
		self.assertContains(first_response, 'earlier.mp4')
		self.assertContains(first_response, 'later.webp')
		self.assertNotContains(first_response, 'other.webp')
		self.assertContains(second_response, 'other.webp')
		self.assertNotContains(second_response, 'earlier.mp4')

	def test_legacy_static_media_is_limited_to_identified_article(self):
		legacy = self.make_post(
			'Original comeback article',
			'watch-this-the-story-of-my-comeback',
		)
		other = self.make_post('Another article', 'another-article')

		migration = import_module(
			'blog.migrations.0004_preserve_legacy_reel_metadata'
		)
		migration.populate_legacy_reel_metadata(
			apps,
			SimpleNamespace(connection=connection),
		)
		legacy.refresh_from_db()
		legacy_response = self.detail(legacy)
		other_response = self.detail(other)

		self.assertContains(legacy_response, 'Recovery Reel')
		self.assertContains(
			legacy_response,
			'Moments from the comeback — rehab, sweat, belief.',
		)
		self.assertContains(legacy_response, 'static/audio/narration.mp3')
		self.assertContains(legacy_response, 'static/video/recovery-1.mp4')
		self.assertNotContains(other_response, 'static/audio/narration.mp3')
		self.assertNotContains(other_response, 'static/video/recovery-1.mp4')
		self.assertNotContains(other_response, 'Recovery Reel')

	def test_legacy_metadata_migration_preserves_custom_values_and_other_posts(self):
		legacy = self.make_post(
			'Original comeback article',
			'watch-this-the-story-of-my-comeback',
		)
		legacy.reel_title = 'My customized title'
		legacy.save(update_fields=['reel_title'])
		other = self.make_post('Another article', 'another-article')
		other.reel_description = 'Do not alter this article.'
		other.save(update_fields=['reel_description'])

		migration = import_module(
			'blog.migrations.0004_preserve_legacy_reel_metadata'
		)
		migration.populate_legacy_reel_metadata(
			apps,
			SimpleNamespace(connection=connection),
		)
		legacy.refresh_from_db()
		other.refresh_from_db()

		self.assertEqual(legacy.reel_title, 'My customized title')
		self.assertEqual(
			legacy.reel_description,
			'Moments from the comeback — rehab, sweat, belief.',
		)
		self.assertEqual(other.reel_title, '')
		self.assertEqual(other.reel_description, 'Do not alter this article.')

	def test_legacy_metadata_migration_succeeds_without_original_post(self):
		other = self.make_post('Another article', 'another-article')
		migration = import_module(
			'blog.migrations.0004_preserve_legacy_reel_metadata'
		)

		migration.populate_legacy_reel_metadata(
			apps,
			SimpleNamespace(connection=connection),
		)

		other.refresh_from_db()
		self.assertEqual(other.reel_title, '')
		self.assertEqual(other.reel_description, '')

	def test_uploaded_reel_media_takes_precedence_over_legacy_fallback(self):
		post = self.make_post(
			'Original comeback article',
			'watch-this-the-story-of-my-comeback',
		)
		PostReelMedia.objects.create(
			post=post,
			media_type=PostReelMedia.IMAGE,
			image='blog/reels/images/uploaded.webp',
		)

		response = self.detail(post)

		self.assertContains(response, 'uploaded.webp')
		self.assertNotContains(response, 'static/video/recovery-1.mp4')
		self.assertNotContains(response, 'static/img/recovery/life.webp')

	def test_narration_is_independent_between_articles(self):
		audio_post = Post.objects.create(
			title='Narrated article',
			slug='narrated-article',
			category='mindset',
			content='Article text',
			narration_audio='blog/narration/narrated.mp3',
		)
		reel_post = self.make_post('Unnarrated reel', 'unnarrated-reel')
		PostReelMedia.objects.create(
			post=reel_post,
			media_type=PostReelMedia.IMAGE,
			image='blog/reels/images/unnarrated.webp',
		)

		audio_response = self.detail(audio_post)
		reel_response = self.detail(reel_post)

		self.assertContains(audio_response, 'narrated.mp3')
		self.assertNotContains(audio_response, 'unnarrated.webp')
		self.assertContains(reel_response, 'unnarrated.webp')
		self.assertNotContains(reel_response, 'narrated.mp3')

	def test_inline_is_registered_for_post_admin(self):
		from .admin import PostAdmin

		self.assertIn(PostReelMediaInline, PostAdmin.inlines)
		self.assertIs(PostReelMediaInline.model, PostReelMedia)

	def test_reel_item_requires_exactly_one_file_matching_its_type(self):
		post = self.make_post('Validation', 'validation')
		item = PostReelMedia(post=post, media_type=PostReelMedia.IMAGE)
		with self.assertRaises(ValidationError):
			item.clean()

		item.image = 'blog/reels/images/image.webp'
		item.video = 'blog/reels/videos/video.mp4'
		with self.assertRaises(ValidationError):
			item.clean()

	def test_upload_validators_check_content_not_only_extension(self):
		invalid_audio = SimpleUploadedFile('narration.mp3', b'not audio')
		invalid_video = SimpleUploadedFile('reel.mp4', b'not video')

		with self.assertRaises(ValidationError):
			validate_audio_upload(invalid_audio)
		with self.assertRaises(ValidationError):
			validate_video_upload(invalid_video)

		validate_audio_upload(SimpleUploadedFile('narration.mp3', b'ID3' + b'\x00' * 13))
		validate_video_upload(SimpleUploadedFile('reel.mp4', b'\x00\x00\x00\x18ftypisom'))
