from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


class BaseTestCase(TestCase):
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


class TestRoutes(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.urls_list = {
            'notes:home': reverse('notes:home'),
            'users:login': reverse('users:login'),
            'users:logout': reverse('users:logout'),
            'users:signup': reverse('users:signup'),
            'notes:list': reverse('notes:list'),
            'notes:add': reverse('notes:add'),
            'notes:success': reverse('notes:success'),
            'notes:detail': reverse('notes:detail', kwargs={'slug': cls.note.slug}),
            'notes:edit': reverse('notes:edit', kwargs={'slug': cls.note.slug}),
            'notes:delete': reverse('notes:delete', kwargs={'slug': cls.note.slug}),
        }

    def test_pages_available_for_all(self):
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                response = self.client.get(self.urls_list[name])
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_pages_available_for_not_auth(self):
        urls = (
            'notes:list',
            'notes:add',
            'notes:success',
        )
        for name in urls:
            with self.subTest(name=name):
                response = self.not_author_user_client.get(
                    self.urls_list[name]
                )
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_available_for_all_types(self):
        urls = (
            'notes:detail',
            'notes:edit',
            'notes:delete',
        )
        for name in urls:
            with self.subTest(name=name):

                response = self.author_user_client.get(
                    self.urls_list[name]
                )
                not_author_user_response = self.not_author_user_client.get(
                    self.urls_list[name]
                )
                not_auth_user_response = self.client.get(
                    self.urls_list[name]
                )

                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertEqual(
                    not_auth_user_response.status_code, HTTPStatus.FOUND)
                self.assertEqual(
                    not_author_user_response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect(self):
        urls = (
            'notes:list',
            'notes:success',
            'notes:add',
            'notes:detail',
            'notes:edit',
            'notes:delete',
        )
        login_url = self.urls_list['users:login']
        for name in urls:
            with self.subTest(name=name):
                response = self.client.get(self.urls_list[name])
                redirect_url = f'{login_url}?next={self.urls_list[name]}'
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertRedirects(response, redirect_url)
