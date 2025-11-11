from django.shortcuts import render, get_object_or_404
from .models import Post

def post_list(request):
    posts = Post.objects.filter(is_published=True)
    context = {
        'posts': posts,
    }
    return render(request, 'blog/list.html', context)


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)
    context = {
        'post': post,
    }
    return render(request, 'blog/detail.html', context)
