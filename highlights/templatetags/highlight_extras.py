from django import template

register = template.Library()

@register.filter
def youtube_embed(url):
    """Convierte un enlace de YouTube normal en un embed."""
    if not url:
        return ""
    if "watch?v=" in url:
        return url.replace("watch?v=", "embed/")
    return url

@register.filter
def vimeo_embed(url):
    """Convierte un enlace de Vimeo normal en un embed."""
    if not url:
        return ""
    if "vimeo.com" in url:
        return url.replace("vimeo.com", "player.vimeo.com/video")
    return url
