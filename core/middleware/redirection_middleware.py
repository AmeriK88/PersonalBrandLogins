from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class CanonicalDomainRedirectMiddleware:
    """
    Redirect requests to the canonical domain in production only.

    Development and testing environments are never redirected.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        environment = getattr(settings, "ENVIRONMENT", "development")

        # Never redirect in development or testing.
        if settings.DEBUG or environment != "production":
            return self.get_response(request)

        canonical = (
            getattr(settings, "CANONICAL_HOST", "")
            .strip()
            .lower()
            .rstrip(".")
        )

        if not canonical:
            return self.get_response(request)

        current_host = request.get_host().split(":")[0].lower().rstrip(".")

        if current_host != canonical:
            return HttpResponsePermanentRedirect(
                f"https://{canonical}{request.get_full_path()}"
            )

        return self.get_response(request)