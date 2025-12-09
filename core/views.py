from django.shortcuts import render
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.conf import settings


def home(request):
    return render(request, "core/home.html")

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        full_message = f"Mensaje de {name} <{email}>:\n\n{message}"

        try:
            send_mail(
                subject=subject,
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=["loginsg00@gmail.com"],  
            )
        except BadHeaderError:
            return HttpResponse("Invalid header found.")
 
        return render(request, "core/contact.html", {
            "success": True
        })

    return render(request, "core/contact.html")

def privacy(request):
    return render(request, "core/privacy.html")

def cookies(request):
    return render(request, "core/cookies.html")
