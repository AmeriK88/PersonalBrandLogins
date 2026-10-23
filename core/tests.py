from smtplib import SMTPException
from unittest.mock import patch

import requests
from django.http import HttpResponse
from django.core import mail
from django.test import RequestFactory, SimpleTestCase, override_settings
from django.urls import reverse

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
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
    RECAPTCHA_SITE_KEY="public-site-key",
    RECAPTCHA_SECRET_KEY="test-secret-key",
    RECAPTCHA_MIN_SCORE=0.5,
    RECAPTCHA_EXPECTED_ACTION="contact_submit",
    RECAPTCHA_ALLOWED_HOSTNAMES=["gloginsjr.com", "www.gloginsjr.com"],
)
class ContactFormTests(SimpleTestCase):
    valid_submission = {
        "name": "Greg Test",
        "email": "person@example.com",
        "subject": "Coaching inquiry",
        "message": "I would like to discuss coaching.",
        "recaptcha_token": "fresh-token",
    }

    valid_verification = {
        "success": True,
        "score": 0.9,
        "action": "contact_submit",
        "hostname": "gloginsjr.com",
    }

    def setUp(self):
        mail.outbox = []

    def post_contact(self, data=None):
        return self.client.post(
            reverse("core:contact"),
            data=data or self.valid_submission,
        )

    @patch("core.recaptcha.requests.post")
    def test_valid_token_sends_existing_formatted_email(self, verify_request):
        verify_request.return_value.json.return_value = self.valid_verification

        response = self.post_contact()

        self.assertContains(response, "Your message has been sent successfully.")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Coaching inquiry")
        self.assertEqual(mail.outbox[0].to, ["loginsg00@gmail.com"])
        self.assertEqual(
            mail.outbox[0].body,
            "Mensaje de Greg Test <person@example.com>:\n\n"
            "I would like to discuss coaching.",
        )
        verify_request.assert_called_once_with(
            "https://www.google.com/recaptcha/api/siteverify",
            data={"secret": "test-secret-key", "response": "fresh-token"},
            timeout=5,
        )

    @patch("core.recaptcha.requests.post")
    def test_missing_token_is_rejected(self, verify_request):
        data = {**self.valid_submission, "recaptcha_token": ""}

        response = self.post_contact(data)

        self.assertContains(response, "We couldn't verify your submission.")
        verify_request.assert_not_called()
        self.assertEqual(mail.outbox, [])

    @patch("core.recaptcha.requests.post")
    def test_invalid_token_is_rejected(self, verify_request):
        verify_request.return_value.json.return_value = {
            **self.valid_verification,
            "success": False,
        }

        response = self.post_contact()

        self.assertContains(response, "We couldn't verify your submission.")
        self.assertEqual(mail.outbox, [])

    @patch("core.recaptcha.requests.post")
    def test_low_score_is_rejected(self, verify_request):
        verify_request.return_value.json.return_value = {
            **self.valid_verification,
            "score": 0.49,
        }

        response = self.post_contact()

        self.assertContains(response, "We couldn't verify your submission.")
        self.assertEqual(mail.outbox, [])

    @patch("core.recaptcha.requests.post")
    def test_incorrect_action_is_rejected(self, verify_request):
        verify_request.return_value.json.return_value = {
            **self.valid_verification,
            "action": "other_action",
        }

        response = self.post_contact()

        self.assertContains(response, "We couldn't verify your submission.")
        self.assertEqual(mail.outbox, [])

    @patch("core.recaptcha.requests.post")
    def test_incorrect_hostname_is_rejected(self, verify_request):
        verify_request.return_value.json.return_value = {
            **self.valid_verification,
            "hostname": "attacker.example",
        }

        response = self.post_contact()

        self.assertContains(response, "We couldn't verify your submission.")
        self.assertEqual(mail.outbox, [])

    @patch("core.recaptcha.requests.post", side_effect=requests.Timeout)
    def test_google_timeout_fails_closed(self, verify_request):
        response = self.post_contact()

        self.assertContains(response, "We couldn't verify your submission.")
        verify_request.assert_called_once()
        self.assertEqual(mail.outbox, [])

    @override_settings(RECAPTCHA_SECRET_KEY="")
    @patch("core.recaptcha.requests.post")
    def test_missing_secret_fails_closed_without_google_request(self, verify_request):
        response = self.post_contact()

        self.assertContains(response, "We couldn't verify your submission.")
        verify_request.assert_not_called()
        self.assertEqual(mail.outbox, [])

    @override_settings(RECAPTCHA_SITE_KEY="")
    @patch("core.recaptcha.requests.post")
    def test_missing_site_key_fails_closed_without_google_request(self, verify_request):
        response = self.post_contact()

        self.assertContains(response, "We couldn't verify your submission.")
        verify_request.assert_not_called()
        self.assertEqual(mail.outbox, [])

    @patch("core.recaptcha.requests.post")
    def test_honeypot_submission_is_rejected_before_verification(self, verify_request):
        response = self.post_contact({**self.valid_submission, "website": "spam"})

        self.assertIn(
            "We couldn't process your message. Please try again.",
            response.context["form"].non_field_errors(),
        )
        verify_request.assert_not_called()
        self.assertEqual(mail.outbox, [])

    @patch("core.recaptcha.requests.post")
    def test_invalid_form_fields_are_rejected_before_verification(self, verify_request):
        data = {
            **self.valid_submission,
            "email": "not-an-email",
            "message": "   ",
        }

        response = self.post_contact(data)

        self.assertContains(response, "Enter a valid email address.")
        self.assertContains(response, "This field is required.")
        verify_request.assert_not_called()
        self.assertEqual(mail.outbox, [])

    @patch("core.recaptcha.requests.post")
    @patch("core.views.send_mail", side_effect=SMTPException("delivery failed"))
    def test_email_delivery_failure_does_not_report_success(
        self, send_email, verify_request
    ):
        verify_request.return_value.json.return_value = self.valid_verification

        response = self.post_contact()

        self.assertIn(
            "We couldn't send your message right now. Please try again later.",
            response.context["form"].non_field_errors(),
        )
        self.assertNotContains(response, "Your message has been sent successfully.")
        send_email.assert_called_once()
        self.assertEqual(mail.outbox, [])

    @patch("core.recaptcha.requests.post")
    def test_malformed_google_response_fails_closed(self, verify_request):
        verify_request.return_value.json.return_value = ["not", "an", "object"]

        response = self.post_contact()

        self.assertContains(response, "We couldn't verify your submission.")
        self.assertEqual(mail.outbox, [])

    def test_contact_page_exposes_only_site_key(self):
        response = self.client.get(reverse("core:contact"))

        self.assertContains(response, "public-site-key")
        self.assertNotContains(response, "test-secret-key")
        self.assertContains(response, 'name="recaptcha_token"')
        self.assertContains(response, 'name="website"')


class CanonicalDomainRedirectTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = CanonicalDomainRedirectMiddleware(
            lambda request: HttpResponse("OK")
        )

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