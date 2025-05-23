from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify


from notes.forms import WARNING
from notes.models import Note
from .base_test import BaseTestLogic

User = get_user_model()


class TestNoteCreation(BaseTestLogic):
    def setUp(self):
        Note.objects.all().delete()

    def test_anonymous_user_cant_create_note(self):
        """Проверка создания заметки анонимным пользователем."""
        notes_count_before = Note.objects.count()
        self.client.post(self.URL_ADD, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, notes_count_before)

    def test_user_can_create_note(self):
        """Проверка создания заметки залогиненным пользователем."""
        notes_count_before = Note.objects.count()
        response = self.auth_client.post(self.URL_ADD, data=self.form_data)
        self.assertRedirects(response, self.URL_SUCCESS)
        note_count = Note.objects.count()
        self.assertEqual(note_count, notes_count_before + 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.user)

    def test_slug(self):
        """Проверка заполнения slug при создании заметки."""
        self.form_data.pop('slug')
        notes_count_before = Note.objects.count()
        response = self.auth_client.post(self.URL_ADD, data=self.form_data)
        self.assertRedirects(response, self.URL_SUCCESS)
        self.assertEqual(Note.objects.count(), notes_count_before + 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(BaseTestLogic):
    def test_unique_slug(self):
        """Проверка уникальности slug."""
        self.form_data['slug'] = 'Slug'
        notes_count_before = Note.objects.count()
        response = self.author_client.post(self.URL_ADD, data=self.form_data)
        self.assertEqual(Note.objects.count(), notes_count_before)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.form_data['slug'] + WARNING)
        )

    def test_author_can_edit_note(self):
        """Проверка возможности редактирования автором своей заметки."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.URL_SUCCESS)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.note.author)

    def test_author_can_delete_note(self):
        """Проверка возможности удаления автором своей заметки."""
        notes_count_before = Note.objects.count()
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, self.URL_SUCCESS)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, notes_count_before - 1)

    def test_user_cant_edit_note_of_another_user(self):
        """Проверка возможности редактирования автором чужой заметки."""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)

    def test_user_cant_delete_note_of_another_user(self):
        """Проверка возможности удаления автором чужой заметки."""
        notes_count_before = Note.objects.count()
        response = self.reader_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, notes_count_before)
