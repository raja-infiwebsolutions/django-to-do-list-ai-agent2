from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),
    
    # Web and API routes
    path("", include("apps.todos.urls")),
    
    # Redirect root to todos list
    path("home/", RedirectView.as_view(url='/todos/', permanent=False)),
]
