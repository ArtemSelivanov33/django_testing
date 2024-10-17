from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author1 = User.objects.create_user(
            username='author1',
            password='password1'
        )
        cls.author2 = User.objects.create_user(
            username='author2',
            password='password2'
        )
        cls.note1 = Note.objects.create(
            title='Заметка автора 1',
            text='Содержимое заметки 1',
            author=cls.author1
        )
        cls.note2 = Note.objects.create(
            title='Заметка автора 2',
            text='Содержимое заметки 2',
            author=cls.author2
        )

    def login_as_author1(self):
        self.client.login(
            username='author1',
            password='password1'
        )

    def test_note_in_context_list(self):
        """Заметки одного пользователя не попадают в заметки другого."""
        self.login_as_author1()
        response = self.client.get(
            reverse('notes:list')
        )
        self.assertIn(
            'object_list',
            response.context
        )
        self.assertIn(
            self.note1,
            response.context['object_list']
        )
        self.assertNotIn(
            self.note2,
            response.context['object_list']
        )

    def test_create_note_form(self):
        """Форма для создания заметки передана в контекст."""
        self.login_as_author1()
        response = self.client.get(
            reverse('notes:add')
        )
        self.assertIn(
            'form',
            response.context
        )

    def test_edit_note_form(self):
        """Форма для редактирования заметки передана в контекст."""
        self.login_as_author1()
        response = self.client.get(
            reverse(
                'notes:edit',
                kwargs={'slug': self.note1.slug}
            )
        )
        self.assertIn(
            'form',
            response.context
        )
