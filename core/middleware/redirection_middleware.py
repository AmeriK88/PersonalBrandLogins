from django.conf import settings
from django.http import HttpResponsePermanentRedirect

class CanonicalDomainRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        canonical = getattr(settings, "CANONICAL_HOST", "")
        if canonical:
            host = request.get_host().split(":")[0]
            if host != canonical:
                return HttpResponsePermanentRedirect(f"https://{canonical}{request.get_full_path()}")
        return self.get_response(request)
