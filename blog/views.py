from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.db.models import Q
from .models import Post

LEGACY_MULTIMEDIA_POST_SLUG = 'watch-this-the-story-of-my-comeback'

def post_list(request):
    posts = Post.objects.filter(is_published=True)
    context = {
        'posts': posts,
    }
    return render(request, 'blog/list.html', context)


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)
    reel_items = list(post.reel_media.filter(
        (Q(media_type='image', video='') & ~Q(image=''))
        | (Q(media_type='video', image='') & ~Q(video=''))
    ))

    # Absolute URL (https://YOUR_DOMAIN.com/blog/YOUR_ROUTE/)
    share_url = request.build_absolute_uri(post.get_absolute_url())

    context = {
        'post': post,
        'share_url': share_url,
        'reel_items': reel_items,
        'legacy_multimedia': post.slug == LEGACY_MULTIMEDIA_POST_SLUG,
    }
    return render(request, 'blog/detail.html', context)
