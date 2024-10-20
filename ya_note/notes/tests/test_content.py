from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from .base_test import BaseTestContent

User = get_user_model()


class TestContent(BaseTestContent):

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
