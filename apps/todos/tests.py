from django.test import TestCase
from django.contrib.auth.models import User
from .models import Todo


class TodoModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test@example.com', email='test@example.com', password='password')

    def test_create_todo(self):
        todo = Todo.objects.create(user=self.user, title='Test', description='desc')
        self.assertEqual(str(todo), 'Test ({})'.format(self.user))
        self.assertFalse(todo.completed)


# Additional tests for views/serializers are in separate integration suites (e2e).