from django.contrib import admin
from django.urls import path, include
from django.conf import settings         
from django.conf.urls.static import static  
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")), 
    path("career/", include("career.urls")),
    path("highlights/", include("highlights.urls")),
    path("blog/", include("blog.urls")), 
    path(
        "service-worker.js",
        TemplateView.as_view(
            template_name="service-worker.js",
            content_type="application/javascript",
        ),
        name="service-worker",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
