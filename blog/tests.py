from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import TestCase, override_settings
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

		legacy_response = self.detail(legacy)
		other_response = self.detail(other)

		self.assertContains(legacy_response, 'static/audio/narration.mp3')
		self.assertContains(legacy_response, 'static/video/recovery-1.mp4')
		self.assertNotContains(other_response, 'static/audio/narration.mp3')
		self.assertNotContains(other_response, 'static/video/recovery-1.mp4')

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
