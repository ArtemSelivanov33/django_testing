
import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from http import HTTPStatus

from news.models import News, Comment


@pytest.mark.django_db
def test_news_count_on_homepage(client):
    """Тест количества новостей на главной странице."""
    for i in range(15):
        News.objects.create(
            title=f'News {i}',
            text='Some content'
        )

    response = client.get(reverse('news:home'))

    assert response.status_code == HTTPStatus.OK
    assert len(response.context['object_list']) <= 10


@pytest.mark.django_db
def test_news_sorted_by_date(client):
    """Тест сортировки новостей."""
    news1 = News.objects.create(
        title='Old News',
        text='Old content',
        date='2023-01-01'
    )
    news2 = News.objects.create(
        title='New News',
        text='New content',
        date='2023-02-01'
    )

    response = client.get(reverse('news:home'))
    news_list = response.context['object_list']

    assert news_list[0] == news2
    assert news_list[1] == news1


@pytest.mark.django_db
def test_comments_sorted_by_date(client):
    """Тест сортировки комментариев."""
    user = User.objects.create_user(
        username='testuser',
        password='testpass'
    )
    news = News.objects.create(
        title='Test News',
        text='Content of test news'
    )
    Comment.objects.create(
        news=news,
        author=user,
        text='Older Comment',
        created='2023-01-01'
    )
    Comment.objects.create(
        news=news,
        author=user,
        text='Newer Comment',
        created='2023-02-01'
    )

    comments_list = news.comment_set.all().order_by('created')

    assert comments_list[0].text == 'Older Comment'
    assert comments_list[1].text == 'Newer Comment'


@pytest.mark.django_db
def test_anonymous_user_cannot_post_comment(client):
    """Тест недоступности формы комментария анонимному пользователю."""
    news = News.objects.create(
        title='Test News',
        text='Content of test news'
    )

    response = client.get(
        reverse(
            'news:detail',
            args=[news.pk]
        )
    )

    assert 'form' not in response.context


@pytest.mark.django_db
def test_authenticated_user_can_post_comment(client):
    """Тест доступности формы комментария авторизованному пользователю."""
    username = 'testuser'
    password = 'password'
    User.objects.create_user(username=username, password=password)
    client.login(
        username='testuser',
        password='password'
    )
    news = News.objects.create(
        title='Test News',
        text='Content of test news'
    )

    response = client.get(
        reverse(
            'news:detail',
            args=[news.pk]
        )
    )

    assert 'form' in response.context
