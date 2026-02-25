from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .models import Post

def post_list(request):
    posts = Post.objects.filter(is_published=True)
    context = {
        'posts': posts,
    }
    return render(request, 'blog/list.html', context)


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)

    # Absolute URL (https://YOUR_DOMAIN.com/blog/YOUR_ROUTE/)
    share_url = request.build_absolute_uri(post.get_absolute_url())

    context = {
        'post': post,
        'share_url': share_url,
    }
    return render(request, 'blog/detail.html', context)
