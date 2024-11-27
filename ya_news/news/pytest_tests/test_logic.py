from http import HTTPStatus

from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Новый текст'


def test_anonymous_user_cant_create_comment(client, news_detail_url):
    initial_comments_count = Comment.objects.count()
    form_data = {'text': COMMENT_TEXT}
    client.post(news_detail_url, data=form_data)
    final_comments_count = Comment.objects.count()
    assert initial_comments_count == final_comments_count


def test_user_can_create_comment(
    author_client,
    author,
    news_detail_url,
    news
):
    Comment.objects.all().delete()
    form_data = {'text': COMMENT_TEXT}
    response = author_client.post(news_detail_url, data=form_data)
    assertRedirects(response, f'{news_detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news_detail_url):
    comments_count_initial = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(news_detail_url, data=bad_words_data)
    comments_count_result = Comment.objects.count()
    assert comments_count_initial == comments_count_result
    form = response.context['form']
    assert 'text' in form.errors
    assert WARNING in form.errors['text']


def test_author_can_edit_comment(
    author_client,
    comment,
    reverse_url,
    news_detail_url,
):
    form_data = {'text': NEW_COMMENT_TEXT}
    response = author_client.post(reverse_url['news:edit'], data=form_data)
    url_to_comments = news_detail_url + '#comments'
    assertRedirects(response, url_to_comments)
    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == form_data['text']
    assert updated_comment.author == comment.author
    assert updated_comment.news == comment.news


def test_user_cant_edit_comment_of_another_user(
        not_author_client,
        comment,
        reverse_url,
):
    form_data = {'text': NEW_COMMENT_TEXT}
    response = not_author_client.post(reverse_url['news:edit'], data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == COMMENT_TEXT
    assert updated_comment.author == comment.author
    assert updated_comment.news == comment.news
