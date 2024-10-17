from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username='author',
            password='authorpassword'
        )
        cls.reader = User.objects.create_user(
            username='reader',
            password='readerpassword'
        )
        cls.note = Note.objects.create(
            title='Заголовок заметки',
            text='Содержимое заметки',
            author=cls.author
        )

    def login_as_author(self):
        self.client.login(
            username='author',
            password='authorpassword'
        )

    def test_home_page_anonymous_user(self):
        """Главная страница доступна анонимному пользователю."""
        response = self.client.get(reverse('notes:home'))
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK
        )

    def test_authenticated_user_access(self):
        """Доступ аутентифицированному пользователю."""
        self.login_as_author()
        accessible_urls = [
            'notes:list',
            'notes:success',
            'notes:add',
        ]

        for url in accessible_urls:
            with self.subTest(url=url):
                response = self.client.get(reverse(url))
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK
                )

    def login_as_reader(self):
        self.client.login(
            username='reader',
            password='readerpassword'
        )

    def test_access_returns_404_for_non_author(self):
        """Доступ не для автора."""
        self.login_as_reader()
        accessible_urls = [
            reverse('notes:detail', kwargs={'slug': self.note.slug}),
            reverse('notes:edit', kwargs={'slug': self.note.slug}),
            reverse('notes:delete', kwargs={'slug': self.note.slug}),
        ]

        for url in accessible_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.NOT_FOUND
                )

    def test_anonymous_user_redirects(self):
        """Тест перенаправления анонимного пользователя."""
        accessible_urls = [
            reverse('notes:list'),
            reverse('notes:success'),
            reverse('notes:add'),
            reverse('notes:detail', kwargs={'slug': self.note.slug}),
            reverse('notes:edit', kwargs={'slug': self.note.slug}),
            reverse('notes:delete', kwargs={'slug': self.note.slug}),
        ]
        for url in accessible_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(
                    response,
                    reverse('users:login') + '?next=' + url
                )

    def test_pages_accessible_to_all(self):
        """Доступ всем пользователям."""
        accessible_urls = [
            'users:login',
            'users:signup',
            'users:logout',
        ]

        for url in accessible_urls:
            with self.subTest(url=url):
                response = self.client.get(reverse(url))
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK
                )
