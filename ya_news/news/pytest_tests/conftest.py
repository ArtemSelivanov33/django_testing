from datetime import datetime, timedelta

import pytest
from django.test import Client
from django.urls import reverse
from django.conf import settings
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def get_news():
    today = datetime.today()
    News.objects.bulk_create(
        News(title=f'News {i}',
             text='Some content',
             date=today - timedelta(days=i))
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Author')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Test News',
        text='Content of test news',
    )
    return news


@pytest.fixture
def get_comments_news(news, author):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Test text {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Text comment',
    )
    return comment


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def url_comments(detail_url):
    return detail_url + '#comments'


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')
