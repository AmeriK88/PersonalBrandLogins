from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, override_settings

from core.middleware.redirection_middleware import (
    CanonicalDomainRedirectMiddleware,
)


class CanonicalDomainMiddlewareTests(SimpleTestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = CanonicalDomainRedirectMiddleware(
            lambda request: HttpResponse("OK")
        )

    @override_settings(
        DEBUG=True,
        ENVIRONMENT="development",
        CANONICAL_HOST="gloginsjr.com",
        ALLOWED_HOSTS=["127.0.0.1", "gloginsjr.com"],
    )
    def test_development_does_not_redirect(self):
        request = self.factory.get(
            "/",
            HTTP_HOST="127.0.0.1:8000",
        )

        response = self.middleware(request)

        self.assertEqual(response.status_code, 200)

    @override_settings(
        DEBUG=False,
        ENVIRONMENT="production",
        CANONICAL_HOST="gloginsjr.com",
        ALLOWED_HOSTS=["www.gloginsjr.com", "gloginsjr.com"],
    )
    def test_production_redirects_to_canonical_domain(self):
        request = self.factory.get(
            "/blog/example/?page=2",
            HTTP_HOST="www.gloginsjr.com",
        )

        response = self.middleware(request)

        self.assertEqual(response.status_code, 301)
        self.assertEqual(
            response["Location"],
            "https://gloginsjr.com/blog/example/?page=2",
        )

    @override_settings(
        DEBUG=False,
        ENVIRONMENT="production",
        CANONICAL_HOST="gloginsjr.com",
        ALLOWED_HOSTS=["gloginsjr.com"],
    )
    def test_canonical_domain_does_not_redirect(self):
        request = self.factory.get(
            "/",
            HTTP_HOST="gloginsjr.com",
        )

        response = self.middleware(request)

        self.assertEqual(response.status_code, 200)

    @override_settings(
        DEBUG=False,
        ENVIRONMENT="development",
        CANONICAL_HOST="gloginsjr.com",
        ALLOWED_HOSTS=["127.0.0.1"],
    )
    def test_development_does_not_redirect_when_debug_is_false(self):
        request = self.factory.get(
            "/",
            HTTP_HOST="127.0.0.1:8000",
        )

        response = self.middleware(request)

        self.assertEqual(response.status_code, 200)