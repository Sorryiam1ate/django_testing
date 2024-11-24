from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from notes.forms import WARNING
from notes.models import Note
from pytils.translit import slugify


class TestLogic(TestCase):

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

        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    @staticmethod
    def get_authenticated_client(user):
        client = Client()
        client.force_login(user)
        return client

    def create_note(self, author):
        return Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=author,
        )

    def test_auth_user_can_create_note(self):
        url = reverse('notes:add')
        response = self.author_user_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])

    def test_anonymous_user_cant_create_note(self):
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_not_unique_slug(self):
        url = reverse('notes:add')
        note = self.create_note(self.author)
        self.form_data['slug'] = note.slug
        response = self.author_user_client.post(url, data=self.form_data)
        self.assertFormError(response, 'form', 'slug',
                             errors=(note.slug + WARNING))
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug_generates_authomatically(self):
        url = reverse('notes:add')
        self.form_data.pop('slug')
        response = self.author_user_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_delete_note(self):
        note = self.create_note(self.author)
        url = reverse('notes:edit', args=(note.slug,))
        response = self.author_user_client.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        note.refresh_from_db()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        note = self.create_note(self.author)
        url = reverse('notes:edit', args=(note.slug,))
        response = self.not_author_user_client.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=note.id)
        self.assertEqual(note.title, note_from_db.title)
        self.assertEqual(note.text, note_from_db.text)
        self.assertEqual(note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        note = self.create_note(self.author)
        url = reverse('notes:delete', args=[note.slug])
        response = self.author_user_client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        note = self.create_note(self.author)
        url = reverse('notes:delete', args=[note.slug])
        response = self.not_author_user_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
