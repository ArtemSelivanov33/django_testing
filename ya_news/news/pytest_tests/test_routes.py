import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from http import HTTPStatus

from news.models import News, Comment

User = get_user_model()


@pytest.mark.django_db
def test_home_page_accessible_to_anonymous_user(client):
    """Главная страница доступна анонимному пользователю."""
    response = client.get(reverse('news:home'))
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_news_detail_accessible_to_anonymous_user(client):
    """Страница отдельной новости доступна анонимному пользователю."""
    news_item = News.objects.create(
        title='Тестовая новость',
        text='Содержимое тестовой новости'
    )

    response = client.get(
        reverse(
            'news:detail',
            args=[news_item.id]
        )
    )

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_delete_comment_accessible_to_comment_author(client):
    """Доступ автора комментария к странице удаления комментария."""
    user = User.objects.create_user(
        username='testuser',
        password='password'
    )
    client.login(
        username='testuser',
        password='password'
    )
    news_item = News.objects.create(
        title='Тестовая новость',
        text='Содержимое тестовой новости'
    )
    comment = Comment.objects.create(
        text='Тестовый комментарий',
        author=user, news=news_item
    )

    response = client.post(
        reverse(
            'news:delete',
            args=[comment.id]
        )
    )

    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.django_db
def test_edit_comment_accessible_to_comment_author(client):
    """Доступ автора комментария к странице редактирования комментария."""
    user = User.objects.create_user(
        username='testuser',
        password='password'
    )
    client.login(
        username='testuser',
        password='password'
    )
    news_item = News.objects.create(
        title='Тестовая новость',
        text='Содержимое тестовой новости'
    )
    comment = Comment.objects.create(
        text='Тестовый комментарий',
        author=user, news=news_item
    )

    response = client.post(
        reverse(
            'news:edit',
            args=[comment.id]
        )
    )

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_anonymous_user_redirected_on_delete_comment(client):
    """Проверка редиректа анонимного пользователя."""
    user = User.objects.create_user(
        username='testuser',
        password='password'
    )
    news_item = News.objects.create(
        title='Тестовая новость',
        text='Содержимое тестовой новости'
    )
    comment = Comment.objects.create(
        text='Тестовый комментарий',
        author=user,
        news=news_item
    )

    response = client.post(
        reverse(
            'news:delete',
            args=[comment.id]
        )
    )

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == '/auth/login/?next=/delete_comment/1/'


@pytest.mark.django_db
def test_anonymous_user_redirected_on_edit_comment(client):
    """Проверка редиректа анонимного пользователя."""
    user = User.objects.create_user(
        username='testuser',
        password='password'
    )
    news_item = News.objects.create(
        title='Тестовая новость',
        text='Содержимое тестовой новости'
    )
    comment = Comment.objects.create(
        text='Тестовый комментарий',
        author=user, news=news_item
    )

    response = client.post(
        reverse(
            'news:edit',
            args=[comment.id]
        )
    )

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == '/auth/login/?next=/edit_comment/1/'


@pytest.mark.django_db
def test_authenticated_user_cannot_edit_other_comment(client):
    """Тест возможности редактировать чужой комментарий."""
    user2 = User.objects.create_user(
        username='testuser2',
        password='password'
    )
    username = 'testuser1'
    password = 'password'
    User.objects.create_user(
        username=username,
        password=password
    )
    client.login(
        username='testuser1',
        password='password'
    )
    news_item = News.objects.create(
        title='Тестовая новость',
        text='Содержимое тестовой новости'
    )
    comment = Comment.objects.create(
        text='Тестовый комментарий',
        author=user2,
        news=news_item
    )

    response = client.post(
        reverse(
            'news:edit',
            args=[comment.id]
        )
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_registration_login_logout_accessible_to_anonymous_user(client):
    """Тест доступности страниц для анонимного пользователя."""
    urls = [
        'users:signup',
        'users:login',
        'users:logout'
    ]

    for url_name in urls:
        response = client.get(reverse(url_name))
        assert response.status_code == HTTPStatus.OK
