from http import HTTPStatus
from pytest_django.asserts import assertRedirects, assertFormError
from django.contrib.auth import get_user_model
from django.urls import reverse
from news.forms import BAD_WORDS, WARNING
from news.models import Comment


User = get_user_model()


def test_anonymous_user_cant_create_comment(client, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    num_of_comments_before_post = Comment.objects.count()
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == num_of_comments_before_post


def test_user_can_create_comment(admin_client, admin_user, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    response = admin_client.post(url, data=form_data)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    redirect = f'{url}#comments'
    assertRedirects(response, redirect)
    news.refresh_from_db()


def test_user_cant_use_bad_words(admin_client, news):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=(news.id,))
    response = admin_client.post(url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, comment, news):
    url = reverse('news:delete', args=(news.id,))
    response = author_client.delete(url)
    redirect_url = reverse('news:detail', args=(news.id,))
    redirect = f'{redirect_url}#comments'
    assertRedirects(response, redirect)
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(admin_client, comment, news):
    url = reverse('news:delete', args=(news.id,))
    response = admin_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_author_can_edit_comment(author_client, news, comment, edit_comment):
    url = reverse('news:edit', args=(news.id,))
    response = author_client.post(url, data=edit_comment)
    redirect_url = reverse('news:detail', args=(news.id,))
    redirect = f'{redirect_url}#comments'
    assertRedirects(response, redirect)
    new_post = Comment.objects.get()
    assert new_post.text == edit_comment['text']


def test_user_cant_edit_comment_of_another_user(
        admin_client, news, comment, edit_comment
):
    url = reverse('news:edit', args=(news.id,))
    response = admin_client.post(url, data=edit_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
