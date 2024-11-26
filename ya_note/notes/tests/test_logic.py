from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note
from pytils.translit import slugify


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(
            username='testuser',
        )
        cls.not_author_user = User.objects.create(
            username='not_author_user',
        )
        cls.author_user_client = cls.get_authenticated_client(
            cls.author
        )
        cls.not_author_user_client = cls.get_authenticated_client(
            cls.not_author_user
        )

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='test-slug',
            author=cls.author,
        )

        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }


class TestLogic(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.urls_list = {
            'notes:list': reverse('notes:list'),
            'notes:detail': reverse(
                'notes:detail',
                kwargs={'slug': cls.note.slug}
            ),
            'notes:add': reverse('notes:add'),
            'notes:edit': reverse(
                'notes:edit',
                kwargs={'slug': cls.note.slug}
            ),
            'notes:delete': reverse(
                'notes:delete',
                kwargs={'slug': cls.note.slug}
            ),
            'notes:success': reverse('notes:success'),
            'users:login': reverse('users:login'),

        }

    @staticmethod
    def get_authenticated_client(user):
        client = Client()
        client.force_login(user)
        return client

    def clear_note_data(self):
        Note.objects.all().delete()

    def test_auth_user_can_create_note(self):
        self.clear_note_data()
        response = self.author_user_client.post(
            self.urls_list['notes:add'], data=self.form_data)
        self.assertRedirects(response, self.urls_list['notes:success'])
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        initial_note_amount = Note.objects.count()
        response = self.client.post(
            self.urls_list['notes:add'],
            data=self.form_data,
        )
        url_login = self.urls_list['users:login']
        url = self.urls_list['notes:add']
        expected_url = (
            f'{url_login}?next={url}'
        )
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), initial_note_amount)

    def test_not_unique_slug(self):
        initial_note_amount = Note.objects.count()
        self.form_data['slug'] = self.note.slug
        response = self.author_user_client.post(
            self.urls_list['notes:add'],
            data=self.form_data,
        )
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING),
        )
        self.assertEqual(
            Note.objects.count(),
            initial_note_amount
        )

    def test_empty_slug_generates_authomatically(self):
        self.clear_note_data()
        self.form_data.pop('slug')
        response = self.author_user_client.post(
            self.urls_list['notes:add'],
            data=self.form_data,
        )
        self.assertRedirects(response, self.urls_list['notes:success'])
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_delete_note(self):

        response = self.author_user_client.post(
            self.urls_list['notes:edit'],
            self.form_data
        )
        self.assertRedirects(response, reverse('notes:success'))
        current_note = Note.objects.get()
        self.assertEqual(current_note.title, self.form_data['title'])
        self.assertEqual(current_note.text, self.form_data['text'])
        self.assertEqual(current_note.slug, self.form_data['slug'])
        self.assertEqual(current_note.author, self.author)

    def test_other_user_cant_edit_note(self):
        response = self.not_author_user_client.post(
            self.urls_list['notes:edit'],
            self.form_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(self.note.author, note_from_db.author)

    def test_author_can_delete_note(self):
        initial_note_amount = Note.objects.count()
        response = self.author_user_client.post(
            self.urls_list['notes:delete']
        )
        self.assertRedirects(
            response,
            self.urls_list['notes:success']
        )
        self.assertEqual(Note.objects.count(), initial_note_amount - 1)

    def test_other_user_cant_delete_note(self):
        initial_note_amount = Note.objects.count()
        response = self.not_author_user_client.post(
            self.urls_list['notes:delete']
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), initial_note_amount)
