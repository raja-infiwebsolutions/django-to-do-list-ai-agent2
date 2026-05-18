from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Todo
import secrets


class TodoModelTest(TestCase):
    """Simple Todo model tests using a runtime-generated test password to avoid
    committing hardcoded credentials into the repository.
    """

    def setUp(self):
        # Generate a per-test random password so no secrets are checked in
        self.TEST_PASSWORD = secrets.token_urlsafe(16)
        User = get_user_model()
        username_field = User.USERNAME_FIELD
        # create_user handles hashing and respects custom USERNAME_FIELD
        self.user = User.objects.create_user(
            **{username_field: "test@example.com"},
            email="test@example.com",
            password=self.TEST_PASSWORD,
        )

    def test_create_todo(self):
        todo = Todo.objects.create(user=self.user, title="Test", description="desc")
        self.assertEqual(str(todo), "Test ({})".format(self.user))
        self.assertFalse(todo.completed)


# Additional tests for views/serializers are in separate integration suites (e2e).