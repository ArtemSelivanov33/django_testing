from http import HTTPStatus

from django.contrib.auth import get_user_model

from .base_test import BaseTestRoutes

User = get_user_model()


class TestRoutes(BaseTestRoutes):
    def test_pages_availability(self):
        """Проверка доступности страниц анон пользователям и всем остальным."""
        for url in self.urls_for_anonymous_access:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_add_and_list(self):
        """Доступ страниц для авторизованного пользователя."""
        for url in self.urls_for_author_access:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_show_and_edit_and_delete(self):
        """Страницы заметки доступные только автору заметки."""
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for url in self.urls_for_author_only:
                with self.subTest(user=user, url=url):
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверка редиректа анонимного пользователя на страницу логина."""
        urls = self.urls_for_author_only + self.urls_for_author_access
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
