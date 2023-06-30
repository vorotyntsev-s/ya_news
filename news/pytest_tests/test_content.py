from django.urls import reverse
from news.models import News, Comment
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
import pytest


def test_news_count_on_page(author_client, all_news):
    response = author_client.get(reverse('news:home'))
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE

def test_news_order(author_client, all_news):
    response = author_client.get(reverse('news:home'))
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comment_order(client, news, comment, author):
    url = reverse('news:detail', args=(news.id,))
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Текст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        response = client.get(url)
        assert 'news' in response.context
        news = response.context['news']
        all_comments = news.comment_set.all()
        assert all_comments[0].created < all_comments[1].created


def test_anonymous_client_has_no_form(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url)
    assert 'form' in response.context
