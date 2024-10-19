import random
from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.models import Comment
from news.forms import BAD_WORDS, WARNING

pytestmark = pytest.mark.django_db


FORMS_DATA = {
    'text': 'Test comment'
}


def test_anonymous_user_cannot_submit_comment(client, detail_url):
    """Тест-Анонимный пользователь не может отправить комментарий."""
    comments_count_before = Comment.objects.count()
    client.post(detail_url, data=FORMS_DATA)
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before


def test_authenticated_user_can_submit_comment(
        author_client,
        detail_url,
        news,
        author
):
    """Тест-Авторизованный пользователь может отправить комментарий."""
    Comment.objects.all().delete()
    comments_count_before = Comment.objects.count()
    response = author_client.post(detail_url, data=FORMS_DATA)
    assertRedirects(response, f'{detail_url}#comments')
    comments_count_after = Comment.objects.count()
    assert comments_count_after - comments_count_before == 1
    comment = Comment.objects.get()
    assert comment.text == FORMS_DATA['text']
    assert comment.news == news
    assert comment.author == author


def test_comment_contains_prohibited_words(author_client, detail_url):
    """Тест на запрещенные слова в комментарии."""
    bad_words = {'text': f'Какой-то текст, '
                         f'{random.choice(BAD_WORDS)},'
                         f'еще текст'
                 }
    comments_count_before = Comment.objects.count()
    response = author_client.post(detail_url, data=bad_words)
    assertFormError(response, form='form', field='text', errors=WARNING)
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before


def test_authenticated_user_can_edit_own_comment(
        author_client,
        edit_url,
        url_comments,
        comment
):
    """Пользователь может редактировать свои комментарии."""
    old_author = comment.author
    old_news = comment.news
    comment_id = comment.id
    response = author_client.post(edit_url, data=FORMS_DATA)
    assertRedirects(response, url_comments)
    updated_comment = Comment.objects.get(id=comment_id)
    assert updated_comment.text == FORMS_DATA['text']
    assert updated_comment.author == old_author
    assert updated_comment.news == old_news


def test_authenticated_user_can_delete_comment(
        author_client,
        delete_url,
        url_comments,
        comment
):
    """Пользователь может удалять свои комментарии."""
    comments_count_before = Comment.objects.count()
    response = author_client.delete(delete_url)
    assertRedirects(response, url_comments)
    comments_count_after = Comment.objects.count()
    assert comments_count_before - comments_count_after == 1


def test_authenticated_user_cannot_edit_others_comment(
        admin_client,
        edit_url,
        comment
):
    """Пользователь не может редактировать чужие комментарии."""
    response = admin_client.post(edit_url, data=FORMS_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == comment.text
    assert updated_comment.author == comment.author
    assert updated_comment.news == comment.news


def test_authenticated_user_cannot_delete_others_comment(
        admin_client,
        delete_url,
        comment
):
    """Пользователь не может удалять чужие комментарии."""
    comments_count_before = Comment.objects.count()
    response = admin_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before
