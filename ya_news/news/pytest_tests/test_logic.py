import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from http import HTTPStatus

from news.models import News, Comment
from news.forms import WARNING


@pytest.mark.django_db
def test_anonymous_user_cannot_submit_comment(client):
    """Тест-Анонимный пользователь не может отправить комментарий."""
    news = News.objects.create(
        title='Test News',
        text='Content of test news'
    )

    response = client.post(
        reverse(
            'news:edit',
            args=[news.pk]
        ),
        data={'text': 'Test comment'}
    )

    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.filter(news=news).count() == 0


@pytest.mark.django_db
def test_authenticated_user_can_submit_comment(client):
    """Тест-Авторизованный пользователь может отправить комментарий."""
    user = User.objects.create_user(
        username='testuser',
        password='testpass'
    )
    news = News.objects.create(
        title='Test News',
        text='Content of test news'
    )
    comment = Comment.objects.create(
        news=news,
        author=user,
        text='Initial Comment'
    )
    client.login(
        username='testuser',
        password='testpass'
    )

    response = client.post(
        reverse(
            'news:edit',
            args=[comment.pk]
        ),
        data={'text': 'Test comment'}
    )

    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.filter(
        news=news,
        author=user,
        text='Test comment'
    ).exists()


@pytest.mark.django_db
def test_comment_contains_prohibited_words(client):
    """Тест на запрещенные слова в комментарии."""
    user = User.objects.create_user(
        username='testuser',
        password='testpass'
    )
    news = News.objects.create(
        title='Test News',
        text='Content of test news'
    )
    comment = Comment.objects.create(
        news=news,
        author=user,
        text='Нормальный комментарий'
    )
    client.login(
        username='testuser',
        password='testpass'
    )

    response = client.post(
        reverse(
            'news:edit',
            args=[comment.pk]
        ),
        data={'text': 'Этот комментарий содержит слово редиска.'}
    )

    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
    form = response.context['form']
    assert 'text' in form.errors
    assert WARNING in form.errors['text']
    comment.refresh_from_db()
    assert comment.text == 'Нормальный комментарий'


@pytest.mark.django_db
def test_authenticated_user_can_edit_own_comment(client):
    """Пользователь может редактировать свои комментарии."""
    user = User.objects.create_user(
        username='testuser',
        password='testpass'
    )
    news = News.objects.create(
        title='Test News',
        text='Content of test news'
    )
    comment = Comment.objects.create(
        news=news,
        author=user,
        text='Initial Comment'
    )
    client.login(
        username='testuser',
        password='testpass'
    )

    response = client.post(
        reverse(
            'news:edit',
            args=[comment.pk]
        ),
        data={'text': 'Updated Comment'}
    )

    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.get(pk=comment.pk).text == 'Updated Comment'


@pytest.mark.django_db
def test_authenticated_user_cannot_edit_others_comment(client):
    """Пользователь не может редактировать чужие комментарии."""
    user1 = User.objects.create_user(
        username='testuser1',
        password='testpass1'
    )
    news = News.objects.create(
        title='Test News',
        text='Content of test news'
    )
    comment = Comment.objects.create(
        news=news,
        author=user1,
        text='User1 Comment'
    )
    username = 'testuser2'
    password = 'password2'
    User.objects.create_user(
        username=username,
        password=password
    )

    client.login(
        username='testuser2',
        password='testpass2'
    )

    response = client.post(
        reverse(
            'news:edit',
            args=[comment.pk]
        ),
        data={'text': 'Malicious Update'}
    )

    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.get(pk=comment.pk).text == 'User1 Comment'
