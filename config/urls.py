from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/signup/", include(([
        path("", include('apps.todos.urls'))
    ], 'auth'))),
    # The todos app exposes viewsets via REST framework router in apps/todos/urls.py when implemented
]
