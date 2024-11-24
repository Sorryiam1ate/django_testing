# news/tests/test_routes.py
from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(
            username='testuser',
        )
        cls.not_author_user = User.objects.create(
            username='not_author_user',
        )

        cls.author_user_client = Client()
        cls.author_user_client.force_login(cls.author)

        cls.not_author_user_client = Client()
        cls.not_author_user_client.force_login(cls.not_author_user)

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='test-slug',
            author=cls.author,
        )

    def test_pages_available_for_all(self):
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_notes_pages_available_for_auth(self):
        urls = (
            'notes:list',
            'notes:add',
            'notes:success',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.not_author_user_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_available_for_author(self):
        urls = (
            'notes:detail',
            'notes:edit',
            'notes:delete',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                response = self.author_user_client.get(url)
                not_author_user_response = self.not_author_user_client.get(url)
                not_auth_user_response = self.client.get(url)

                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertEqual(
                    not_auth_user_response.status_code, HTTPStatus.FOUND)
                self.assertEqual(
                    not_author_user_response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect(self):
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', {'slug': 'test-slug'}),
            ('notes:edit', {'slug': 'test-slug'}),
            ('notes:delete', {'slug': 'test-slug'}),
        )
        login_url = reverse('users:login')
        for name, args in urls:
            with self.subTest(name=name):
                if args:
                    url = reverse(name, kwargs=args)
                else:
                    url = reverse(name)
                response = self.client.get(url)
                redirect_url = f'{login_url}?next={url}'
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertRedirects(response, redirect_url)
