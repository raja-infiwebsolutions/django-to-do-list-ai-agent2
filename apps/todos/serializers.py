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

    def get_name(self, obj):
        parts = []
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

    def validate_name(self, value):
        name = (value or "").strip()
        if not name:
            raise serializers.ValidationError("Name is required.")
        return name

    def validate_email(self, value):
        # Normalize and ensure uniqueness (case-insensitive)
        email = (value or "").strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email

    def validate_password(self, value):
        # Use Django's built-in password validators where configured
        try:
            django_validate_password(value)
        except Exception as exc:
            messages = getattr(exc, "messages", None) or [str(exc)]
            raise serializers.ValidationError(messages)
        return value

    def create(self, validated_data):
        name = validated_data.get("name", "").strip()
        email = validated_data.get("email").strip().lower()
        password = validated_data.get("password")

        # Use email as username for compatibility with default auth
        username = email

        first_name = ""
        last_name = ""
        parts = name.split()
        if parts:
            first_name = parts[0]
            if len(parts) > 1:
                last_name = " ".join(parts[1:])

        try:
            with transaction.atomic():
                # create_user will handle password hashing
                user = User.objects.create_user(username=username, email=email, password=password)
                # populate first/last name and save
                if first_name:
                    user.first_name = first_name
                if last_name:
                    user.last_name = last_name
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

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError("Must include 'email' and 'password'.")

        email_norm = (email or "").strip().lower()
        # authenticate expects username by default; our username is the email
        user = authenticate(username=email_norm, password=password)

        if not user:
            # Provide a generic error to avoid leaking which part failed
            raise serializers.ValidationError("Unable to log in with provided credentials.")

        if not user.is_active:
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

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Title is required.")
        return value.strip()

    def validate(self, attrs):
        # Ensure required title exists (in case partial updates are allowed elsewhere)
        if self.instance is None and not attrs.get("title"):
            raise serializers.ValidationError({"title": "Title is required."})
        return attrs
