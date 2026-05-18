from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Todo
from .services import TodoService
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


class TodoServiceTest(TestCase):
    def setUp(self):
        self.TEST_PASSWORD = secrets.token_urlsafe(16)
        User = get_user_model()
        username_field = User.USERNAME_FIELD
        self.user = User.objects.create_user(
            **{username_field: "svc@example.com"},
            email="svc@example.com",
            password=self.TEST_PASSWORD,
        )

    def test_create_todo_valid(self):
        payload = {"title": "Svc Todo", "description": "service desc", "completed": "true", "priority": 2}
        todo = TodoService.create_todo(self.user, payload)
        self.assertIsInstance(todo, Todo)
        self.assertEqual(todo.title, "Svc Todo")
        self.assertTrue(todo.completed)
        self.assertEqual(todo.priority, 2)

    def test_create_todo_invalid_completed(self):
        payload = {"title": "Bad Bool", "completed": "maybe"}
        with self.assertRaises(ValidationError):
            TodoService.create_todo(self.user, payload)

    def test_list_todos_empty_returns_page0(self):
        # Ensure user has no todos
        res = TodoService.list_todos(self.user, page=1, limit=10)
        self.assertIn("items", res)
        self.assertIn("meta", res)
        self.assertEqual(res["items"], [])
        self.assertEqual(res["meta"]["page"], 0)
        self.assertEqual(res["meta"]["pages"], 0)

    def test_get_update_delete_flow(self):
        # create
        payload = {"title": "Flow Todo", "description": "flow", "completed": False}
        todo = TodoService.create_todo(self.user, payload)
        # get
        fetched = TodoService.get_todo(self.user, todo.id)
        self.assertEqual(fetched.id, todo.id)
        # update
        updated = TodoService.update_todo(self.user, todo.id, {"title": "Updated", "completed": "1"})
        self.assertEqual(updated.title, "Updated")
        self.assertTrue(updated.completed)
        # delete
        TodoService.delete_todo(self.user, todo.id)
        with self.assertRaises(Todo.DoesNotExist):
            Todo.objects.get(pk=todo.id)
