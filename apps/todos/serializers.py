from typing import Any, Dict, List, Optional, Tuple

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password as django_validate_password
from django.db import IntegrityError, transaction
from rest_framework import serializers
from .models import Todo

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Public user serializer that avoids exposing sensitive fields.

    Adds a `name` field that concatenates first_name and last_name for frontend convenience.
    """

    name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        # Expose basic non-sensitive user fields. Password should never be exposed.
        fields = ["id", "username", "email", "first_name", "last_name", "name"]
        read_only_fields = ["id", "username", "email", "first_name", "last_name", "name"]

    def get_name(self, obj: User) -> str:
        parts: List[str] = []
        if getattr(obj, "first_name", None):
            parts.append(obj.first_name)
        if getattr(obj, "last_name", None):
            parts.append(obj.last_name)
        return " ".join(parts).strip()


class SignupSerializer(serializers.Serializer):
    """Serializer for user signup.

    Enforces required name/email/password and leverages Django's password validators.
    Prevents duplicate emails and ensures email normalization.
    """

    name = serializers.CharField(max_length=150, required=True, allow_blank=False)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_name(self, value: str) -> str:
        name = (value or "").strip()
        if not name:
            raise serializers.ValidationError("Name is required.")
        return name

    def validate_email(self, value: str) -> str:
        # Normalize and ensure uniqueness (case-insensitive)
        email = (value or "").strip().lower()
        username_field = getattr(User, "USERNAME_FIELD", "username")

        # Prefer to check the email field if it exists on the model
        if hasattr(User, "email"):
            lookup = {"email__iexact": email}
        else:
            # fallback to username field uniqueness check
            lookup = {f"{username_field}__iexact": email}

        if User.objects.filter(**lookup).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email

    def validate_password(self, value: str) -> str:
        # Use Django's built-in password validators where configured
        try:
            django_validate_password(value)
        except Exception as exc:
            messages = getattr(exc, "messages", None) or [str(exc)]
            raise serializers.ValidationError(messages)
        return value

    def create(self, validated_data: Dict[str, Any]) -> User:
        name = validated_data.get("name", "").strip()
        email = validated_data.get("email").strip().lower()
        password = validated_data.get("password")

        username_field = getattr(User, "USERNAME_FIELD", "username")

        # Prepare first_name, last_name
        first_name = ""
        last_name = ""
        parts = name.split()
        if parts:
            first_name = parts[0]
            if len(parts) > 1:
                last_name = " ".join(parts[1:])

        try:
            with transaction.atomic():
                # Use create_user when available since it handles hashing and other internals
                manager = getattr(User, "objects", None)
                if manager and hasattr(manager, "create_user"):
                    # Respect common custom user models that use email as username
                    if username_field == "email":
                        user = manager.create_user(email=email, password=password)
                    else:
                        # If username exists separately, set username to email for uniqueness
                        # Some custom models require a username field
                        try:
                            user = manager.create_user(username=email, email=email, password=password)
                        except TypeError:
                            # Fallback for create_user signatures that differ
                            user = manager.create_user(email=email, password=password)
                else:
                    # Fallback for unconventional user managers
                    user_kwargs: Dict[str, Any] = {username_field: email}
                    if hasattr(User, "email"):
                        user_kwargs["email"] = email
                    user = User(**user_kwargs)
                    user.set_password(password)
                    user.save()

                # populate first/last name and save
                if first_name:
                    setattr(user, "first_name", first_name)
                if last_name:
                    setattr(user, "last_name", last_name)
                user.save()
                return user
        except IntegrityError:
            # Race condition / duplicate username/email
            raise serializers.ValidationError({"email": "A user with this email already exists."})


class LoginSerializer(serializers.Serializer):
    """Serializer for user login.

    Expects email and password. On successful validation attaches `user` to validated_data.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError("Must include 'email' and 'password'.")

        email_norm = (email or "").strip().lower()
        request = self.context.get("request")

        # First try authenticating by username (many apps use email as username)
        user = authenticate(request=request, username=email_norm, password=password)

        # If authentication failed, try passing email kwarg (some backends support it)
        if not user:
            try:
                user = authenticate(request=request, email=email_norm, password=password)
            except Exception:
                user = None

        if not user:
            # Provide a generic error to avoid leaking which part failed
            raise serializers.ValidationError("Unable to log in with provided credentials.")

        if not getattr(user, "is_active", True):
            raise serializers.ValidationError("User account is disabled.")

        attrs["user"] = user
        return attrs


class TodoSerializer(serializers.ModelSerializer):
    """Serializer for Todo model.

    - user is read-only and populated from request.user in the views.
    - created_at and updated_at are read-only.
    """

    user = UserSerializer(read_only=True)

    class Meta:
        model = Todo
        fields = [
            "id",
            "user",
            "title",
            "description",
            "status",
            "priority",
            "due_date",
            "completed",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def validate_title(self, value: str) -> str:
        if not value or not value.strip():
            raise serializers.ValidationError("Title is required.")
        return value.strip()

    def _extract_choice_values(self, choices: Optional[List[Tuple[Any, Any]]]) -> List[Any]:
        if not choices:
            return []
        return [c[0] for c in choices]

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        # Ensure required title exists on creation
        if self.instance is None and not attrs.get("title"):
            raise serializers.ValidationError({"title": "Title is required."})

        # Validate choices for status and priority if model exposes them
        errors: Dict[str, Any] = {}

        # Validate status choices
        try:
            status_field = Todo._meta.get_field("status")
            status_choices = self._extract_choice_values(getattr(status_field, "choices", None))
        except Exception:
            status_choices = []

        status_val = attrs.get("status")
        if status_val is not None and status_choices:
            if status_val not in status_choices:
                errors["status"] = f"Invalid status. Allowed values: {status_choices}"

        # Validate priority choices
        try:
            priority_field = Todo._meta.get_field("priority")
            priority_choices = self._extract_choice_values(getattr(priority_field, "choices", None))
        except Exception:
            priority_choices = []

        priority_val = attrs.get("priority")
        if priority_val is not None and priority_choices:
            if priority_val not in priority_choices:
                errors["priority"] = f"Invalid priority. Allowed values: {priority_choices}"

        if errors:
            raise serializers.ValidationError(errors)

        return attrs
