from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class BaseTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Создание общих фикстур для всех тестов."""
        cls.author = User.objects.create(username='Пользователь')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )
        cls.reader = User.objects.create(username='Аноним')

        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))


class TestContent(BaseTestCase):

    def test_notes_list_for_anon_user(self):
        response = self.reader_client.get(self.list_url)
        notes = response.context['object_list']
        self.assertNotIn(self.note, notes)

    def test_notes_list_for_auth_user(self):
        response = self.author_client.get(self.list_url)
        notes = response.context['object_list']
        self.assertIn(self.note, notes)

    def test_edit_and_add_note_pages_contains_form(self):
        """Проверка передачи формы в контекст."""
        urls = (
            self.add_url,
            self.edit_url
        )
        for url in urls:
            response = self.author_client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)
