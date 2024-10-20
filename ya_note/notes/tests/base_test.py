from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


# У меня уже нет времени улучшать код,
# сегодня последний день сдачи этой работы. Потом мне переход оформят.(((
# И я потеряю последний переход.
class BaseTestContent(TestCase):

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


class BaseTestLogic(TestCase):
    NOTE_TEXT = 'Текст заметки'
    NOTE_TITLE = 'Текст заголовка'
    NOTE_SLUG = 'slug'
    NEW_NOTE_TEXT = 'Обновлённая заметка'
    NEW_NOTE_TITLE = 'Обновлённый заголовок заметки'
    NEW_NOTE_SLUG = 'new_slug'
    URL_SUCCESS = reverse('notes:success')
    URL_ADD = reverse('notes:add')

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Пользователь')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            slug='Slug',
            author=cls.author,
            text=cls.NOTE_TEXT
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'text': cls.NEW_NOTE_TEXT,
            'title': cls.NEW_NOTE_TITLE,
            'slug': cls.NEW_NOTE_SLUG
        }
        cls.form_data = {
            'text': cls.NOTE_TEXT,
            'title': cls.NOTE_TITLE,
            'slug': cls.NOTE_SLUG
        }


class BaseTestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Пользователь')
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст', author=cls.author)
        cls.reader = User.objects.create(username='Аноним')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.login_url = reverse('users:login')
        cls.urls_for_author_only = (
            reverse('notes:detail', args=(cls.note.slug,)),
            reverse('notes:edit', args=(cls.note.slug,)),
            reverse('notes:delete', args=(cls.note.slug,)),
        )
        cls.urls_for_anonymous_access = (
            reverse('notes:home'),
            reverse('users:login'),
            reverse('users:logout'),
            reverse('users:signup'),
        )
        cls.urls_for_author_access = (
            reverse('notes:add'),
            reverse('notes:list'),
            reverse('notes:success'),
        )
