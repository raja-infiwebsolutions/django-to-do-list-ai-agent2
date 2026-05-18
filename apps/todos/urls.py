"""
URLs for the `todos` app.

This module exists to satisfy Django's include('apps.todos.urls') import from
config/urls.py. It intentionally defines an empty urlpatterns list so the project
can import the module even if the app has no public-facing URL patterns yet.

Add view imports and URL patterns here as the todos app is developed.
"""
from django.urls import path

urlpatterns = []
