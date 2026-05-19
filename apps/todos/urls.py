"""
URLs for the `todos` app.

Includes:
- Web-based views for HTML rendering (templates)
- REST API endpoints for JSON responses
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, web_views

# DRF Router for ViewSet-based API endpoints
router = DefaultRouter()
router.register(r'todos-api', views.TodoViewSet, basename='todo-api')

# Web-based URL patterns (HTML templates)
web_patterns = [
    path('', web_views.index, name='index'),
    path('login/', web_views.login_view, name='login'),
    path('signup/', web_views.signup_view, name='signup'),
    path('logout/', web_views.logout_view, name='logout'),
]

todos_patterns = [
    path('', web_views.todo_list, name='list'),
    path('create/', web_views.todo_create, name='create'),
    path('<int:todo_id>/edit/', web_views.todo_edit, name='edit'),
    path('<int:todo_id>/delete/', web_views.todo_delete, name='delete'),
    path('<int:todo_id>/toggle/', web_views.todo_toggle, name='toggle'),
    path('stats/', web_views.todo_stats, name='stats'),
]

urlpatterns = [
    # Authentication web routes
    path('auth/', include((web_patterns, 'auth'))),
    
    # Todos web routes
    path('todos/', include((todos_patterns, 'todos'))),
    
    # REST API endpoints
    path('api/', include(router.urls)),
    path('api/auth/signup/', views.SignupView.as_view(), name='api-signup'),
    path('api/auth/login/', views.LoginView.as_view(), name='api-login'),
]
