import pytest
from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db

FORM = 'form'
NEWS = 'news'


def test_news_count_on_homepage(client, get_news, home_url):
    """Тест количества новостей на главной странице."""
    response = client.get(home_url)
    news_count = response.context['object_list'].count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_sorted_by_date(client, get_news, home_url):
    """Тест сортировки новостей."""
    response = client.get(home_url)
    news_get_all = [news.date for news in response.context['object_list']]
    news_sort = sorted(news_get_all, reverse=True)
    assert news_get_all == news_sort


def test_comments_sorted_by_date(client, news, get_comments_news, detail_url):
    """Тест сортировки комментариев."""
    response = client.get(detail_url)
    assert NEWS in response.context
    news_instance = response.context[NEWS]
    comments = list(news_instance.comment_set.all())
    sorted_comments = sorted(comments, key=lambda comment: comment.created)
    assert comments == sorted_comments


def test_anonymous_user_not_available_form_comment(client, news, detail_url):
    """Тест недоступности формы комментария анонимному пользователю."""
    response = client.get(detail_url)
    assert FORM not in response.context


def test_authenticated_user_available_form_comment(author_client, detail_url):
    """Тест доступности формы комментария авторизованному пользователю."""
    response = author_client.get(detail_url)
    assert FORM in response.context
    assert isinstance(response.context[FORM], CommentForm)
