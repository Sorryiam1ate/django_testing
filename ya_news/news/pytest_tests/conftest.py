from datetime import timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Новый текст'


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    note = News.objects.create(
        title='Новость',
        text='Текст новости',
    )
    return note


@pytest.fixture
def news_detail_url(news):
    url = reverse('news:detail', args=(news.id,))
    return url


@pytest.fixture
def news_order_check(author, news):
    today = timezone.now()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def comments_order_check(author, news):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text=COMMENT_TEXT,
    )
    return comment


@pytest.fixture
def edit_comment_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def news_detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def reverse_url(comment):
    return {
        'news:home': reverse('news:home'),
        'users:login': reverse('users:login'),
        'users:logout': reverse('users:logout'),
        'users:signup': reverse('users:signup'),
        'news:edit': reverse('news:edit', args=(comment.id,)),
        'news:delete': reverse('news:delete', args=(comment.id,)),
    }
