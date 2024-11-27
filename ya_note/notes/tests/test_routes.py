from http import HTTPStatus

from notes.tests.conftest import BaseTestCase


class TestRoutes(BaseTestCase):

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
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                )

            with self.subTest(name=name):
                not_author_user_response = self.not_author_user_client.get(
                    self.urls_list[name]
                )
                self.assertEqual(
                    not_author_user_response.status_code,
                    HTTPStatus.NOT_FOUND
                )

            with self.subTest(name=name):
                not_auth_user_response = self.client.get(
                    self.urls_list[name]
                )
                self.assertEqual(
                    not_auth_user_response.status_code,
                    HTTPStatus.FOUND
                )

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
