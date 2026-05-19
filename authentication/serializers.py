"""Serializers for user signup and login.

This module provides SignupSerializer and LoginSerializer used by the
authentication views. It uses get_user_model() to remain compatible with
custom user models and ensures passwords are hashed via set_password.

Validation includes normalization (strip/lowercase) of email, uniqueness
check on signup, and centralized credential validation on login.
"""
from typing import Any, Dict

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework import serializers

User = get_user_model()


class SignupSerializer(serializers.Serializer):
    """Serializer for creating a new user account.

    Ensures name is non-empty, email is normalized and unique, and the
    password is stored hashed using the user model's set_password.
    """

    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_name(self, value: str) -> str:
        """Normalize and validate the name field (no empty/whitespace-only)."""
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Name cannot be empty or whitespace.")
        return value

    def validate_email(self, value: str) -> str:
        """Normalize email and ensure uniqueness (case-insensitive).

        Raises:
            serializers.ValidationError: if a user with the email already exists.
        """
        email = (value or "").strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return email

    def create(self, validated_data: Dict[str, Any]) -> User:
        """Create and return a new user instance with a hashed password.

        Uses a transaction to avoid race conditions leading to IntegrityError.
        The method attempts to set a username derived from the email if the
        user model has a username field.
        """
        name = validated_data.get("name", "").strip()
        email = validated_data["email"]
        password = validated_data["password"]

        # Derive a username from email if the user model has a username field
        username = None
        try:
            user_fields = {f.name for f in User._meta.get_fields()}
        except Exception:
            user_fields = set()

        if "username" in user_fields:
            username = email.split("@")[0]

        try:
            with transaction.atomic():
                if hasattr(User.objects, "create_user"):
                    # Prefer create_user if available (it usually handles set_password)
                    if username is not None:
                        user = User.objects.create_user(username=username, email=email, password=password)
                        # set first/last name if model supports these
                        if hasattr(user, "first_name"):
                            user.first_name = name
                            user.save()
                    else:
                        user = User.objects.create_user(email=email, password=password)
                        if hasattr(user, "first_name"):
                            user.first_name = name
                            user.save()
                else:
                    # Fallback: manually construct user and set password
                    create_kwargs = {"email": email}
                    if username is not None:
                        create_kwargs["username"] = username
                    user = User(**create_kwargs)
                    if hasattr(user, "first_name"):
                        user.first_name = name
                    user.set_password(password)
                    user.save()
        except IntegrityError:
            # Rare race condition where another process created the same email
            raise serializers.ValidationError("A user with that email already exists.")

        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for authenticating users by email and password.

    The validate() method centralizes credential checks and returns the
    authenticated user instance in validated_data['user'] on success.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value: str) -> str:
        """Normalize email for consistent lookup."""
        return (value or "").strip().lower()

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate credentials and attach the user to attrs on success.

        Raises:
            serializers.ValidationError: when credentials are invalid.
        """
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials.")

        if not getattr(user, "is_active", True):
            raise serializers.ValidationError("User account is disabled.")

        attrs["user"] = user
        return attrs
