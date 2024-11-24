from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from notes.forms import NoteForm
from notes.models import Note


class TestContent(TestCase):
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

    def test_note_in_list_for_author(self):
        url = reverse('notes:list')
        response = self.author_user_client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_list_for_another_user(self):
        url = reverse('notes:list')
        response = self.not_author_user_client.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_edit_create_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', {'slug': 'test-slug'}),
        )
        for name, args in urls:
            with self.subTest(name=name):
                if args:
                    url = reverse(name, kwargs=args)
                else:
                    url = reverse(name)
                response = self.author_user_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
