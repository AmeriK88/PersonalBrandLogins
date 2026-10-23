import requests
from django.conf import settings


RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
RECAPTCHA_TIMEOUT_SECONDS = 5


def verify_recaptcha(token):
    site_key = settings.RECAPTCHA_SITE_KEY
    secret_key = settings.RECAPTCHA_SECRET_KEY
    min_score = settings.RECAPTCHA_MIN_SCORE
    allowed_hostnames = settings.RECAPTCHA_ALLOWED_HOSTNAMES

    if (
        not isinstance(token, str)
        or not token.strip()
        or not isinstance(site_key, str)
        or not site_key
        or not isinstance(secret_key, str)
        or not secret_key
        or isinstance(min_score, bool)
        or not isinstance(min_score, (int, float))
        or not 0 <= min_score <= 1
        or not isinstance(allowed_hostnames, (list, tuple, set))
        or not allowed_hostnames
    ):
        return False

    try:
        response = requests.post(
            RECAPTCHA_VERIFY_URL,
            data={"secret": secret_key, "response": token},
            timeout=RECAPTCHA_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        result = response.json()
    except (requests.RequestException, ValueError):
        return False

    if not isinstance(result, dict):
        return False

    score = result.get("score")
    hostname = result.get("hostname")
    if not isinstance(hostname, str):
        return False

    allowed = {
        host.lower().rstrip(".")
        for host in allowed_hostnames
        if isinstance(host, str)
    }

    return (
        result.get("success") is True
        and isinstance(score, (int, float))
        and not isinstance(score, bool)
        and 0 <= score <= 1
        and score >= min_score
        and result.get("action") == settings.RECAPTCHA_EXPECTED_ACTION
        and hostname.lower().rstrip(".") in allowed
    )
