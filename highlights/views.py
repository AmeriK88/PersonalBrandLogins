import re
from urllib.parse import parse_qs, urlencode, urlparse

from django.shortcuts import render

from .models import Highlight


YOUTUBE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")
VIMEO_ID_PATTERN = re.compile(r"^\d+$")


def _safe_external_url(value):
    if not value:
        return ""

    try:
        parsed = urlparse(value)
        if (
            parsed.scheme.lower() not in {"http", "https"}
            or not parsed.hostname
            or parsed.username
            or parsed.password
        ):
            return ""
    except ValueError:
        return ""

    return value


def _video_embed_url(value):
    safe_url = _safe_external_url(value)
    if not safe_url:
        return ""

    parsed = urlparse(safe_url)
    hostname = (parsed.hostname or "").lower().rstrip(".")
    if hostname in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
        video_id = ""
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [""])[0]
        else:
            path_parts = parsed.path.strip("/").split("/")
            if len(path_parts) == 2 and path_parts[0] in {"embed", "shorts", "live"}:
                video_id = path_parts[1]

        if YOUTUBE_ID_PATTERN.fullmatch(video_id):
            return f"https://www.youtube-nocookie.com/embed/{video_id}"

    if hostname == "youtu.be":
        video_id = parsed.path.strip("/")
        if YOUTUBE_ID_PATTERN.fullmatch(video_id):
            return f"https://www.youtube-nocookie.com/embed/{video_id}"

    if hostname in {"vimeo.com", "www.vimeo.com", "player.vimeo.com"}:
        path_parts = parsed.path.strip("/").split("/")
        video_id = ""
        privacy_hash = ""
        if hostname == "player.vimeo.com":
            if len(path_parts) == 2 and path_parts[0] == "video":
                video_id = path_parts[1]
        elif path_parts and VIMEO_ID_PATTERN.fullmatch(path_parts[-1]):
            video_id = path_parts[-1]
        elif (
            len(path_parts) == 2
            and VIMEO_ID_PATTERN.fullmatch(path_parts[0])
            and re.fullmatch(r"[A-Za-z0-9]+", path_parts[1])
        ):
            video_id, privacy_hash = path_parts

        if video_id and VIMEO_ID_PATTERN.fullmatch(video_id):
            embed_url = f"https://player.vimeo.com/video/{video_id}"
            if privacy_hash:
                embed_url = f"{embed_url}?{urlencode({'h': privacy_hash})}"
            return embed_url

    return ""


def _image_url(highlight):
    if not highlight.image or not highlight.image.name:
        return ""
    try:
        return highlight.image.url
    except (OSError, ValueError):
        return ""


def highlights_gallery(request):
    photos = Highlight.objects.filter(category='photo')
    videos = Highlight.objects.filter(category='video')
    press = Highlight.objects.filter(category='press')

    hero_image = ""
    for highlight in (*videos, *photos):
        highlight.archive_image_url = _image_url(highlight)
        if highlight.archive_image_url:
            hero_image = highlight.archive_image_url
            break

    for highlight in (*photos, *videos, *press):
        if not hasattr(highlight, "archive_image_url"):
            highlight.archive_image_url = _image_url(highlight)
        highlight.safe_video_url = _safe_external_url(highlight.video_url)
        highlight.video_embed_url = _video_embed_url(highlight.video_url)
        highlight.safe_press_link = _safe_external_url(highlight.press_link)

    context = {
        'photos': photos,
        'videos': videos,
        'press': press,
        'hero_image': hero_image,
    }
    return render(request, 'highlights/gallery.html', context)
