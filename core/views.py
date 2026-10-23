from django.shortcuts import render
from django.core.mail import BadHeaderError, send_mail
from django.conf import settings
from smtplib import SMTPException

from .forms import ContactForm
from .recaptcha import verify_recaptcha


def home(request):
    return render(request, "core/home.html")

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    form = ContactForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            if form.cleaned_data["website"]:
                form.add_error(None, "We couldn't process your message. Please try again.")
            elif not verify_recaptcha(form.cleaned_data["recaptcha_token"]):
                form.add_error(
                    None,
                    "We couldn't verify your submission. Please try again.",
                )
            else:
                name = form.cleaned_data["name"]
                email = form.cleaned_data["email"]
                subject = form.cleaned_data["subject"]
                message = form.cleaned_data["message"]
                full_message = f"Mensaje de {name} <{email}>:\n\n{message}"

                try:
                    sent_count = send_mail(
                        subject=subject,
                        message=full_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=["loginsg00@gmail.com"],
                    )
                except (BadHeaderError, SMTPException, OSError):
                    sent_count = 0

                if sent_count == 1:
                    return render(
                        request,
                        "core/contact.html",
                        {
                            "form": ContactForm(),
                            "success": True,
                            "recaptcha_site_key": settings.RECAPTCHA_SITE_KEY,
                        },
                    )

                form.add_error(
                    None,
                    "We couldn't send your message right now. Please try again later.",
                )

    return render(
        request,
        "core/contact.html",
        {
            "form": form,
            "recaptcha_site_key": settings.RECAPTCHA_SITE_KEY,
        },
    )

def privacy(request):
    return render(request, "core/privacy.html")

def cookies(request):
    return render(request, "core/cookies.html")
