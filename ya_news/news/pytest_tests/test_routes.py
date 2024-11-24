from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name',
    (
        'news:home',
        'users:login',
        'users:logout',
        'users:signup',
    )
)
def test_pages_availability_for_anonymous_user(client, name, reverse_url):
    url = reverse_url[name]
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_detail_page_availability_for_anonymous_user(client, news_detail_url):
    response = client.get(news_detail_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete',)
)
def test_delete_edit_comment_page_available_for_author(
    author_client,
    comment,
    name,
):
    url = reverse(name, args=(comment.id,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'reverse_name, user, status', [
        ('news:edit', pytest.lazy_fixture('client'), 302),
        ('news:delete', pytest.lazy_fixture('client'), 302),
        ('news:edit', pytest.lazy_fixture('not_author_client'), 404),
        ('news:delete', pytest.lazy_fixture('not_author_client'), 404),
    ]
)
def test_redirects(reverse_name, user, status, reverse_url):
    login_url = reverse_url['users:login']
    url = reverse_url[reverse_name]
    expected_url = f'{login_url}?next={url}'
    response = user.get(url)
    if status == 302:
        assert response.status_code == status
        assertRedirects(response, expected_url)
    else:
        assert response.status_code == HTTPStatus.NOT_FOUND
