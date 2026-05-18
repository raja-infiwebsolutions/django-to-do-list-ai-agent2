from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from .models import Todo
from .serializers import (
    SignupSerializer,
    LoginSerializer,
    UserSerializer,
    TodoSerializer,
)


class SignupView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                {"success": True, "message": "User created", "data": {"user": UserSerializer(user).data, "token": token.key}},
                status=status.HTTP_201_CREATED,
            )
        return Response({"success": False, "message": "Validation failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"success": False, "message": "Invalid input", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        # authenticate expects username by default; we use email as username
        user = authenticate(request, username=email, password=password)
        if user is None:
            return Response({"success": False, "message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"success": True, "message": "Login successful", "data": {"user": UserSerializer(user).data, "token": token.key}})


class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Todo.objects.filter(user=self.request.user)
        status_param = self.request.query_params.get("status")
        if status_param:
            if status_param == "completed":
                qs = qs.filter(completed=True)
            elif status_param == "incomplete":
                qs = qs.filter(completed=False)
        return qs.select_related("user")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"])  # example extra action
    def stats(self, request):
        total = Todo.objects.filter(user=request.user).count()
        completed = Todo.objects.filter(user=request.user, completed=True).count()
        return Response({"success": True, "data": {"total": total, "completed": completed}})