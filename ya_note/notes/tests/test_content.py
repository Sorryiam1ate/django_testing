from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
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

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='test-slug',
            author=cls.author,
        )

        cls.author_user_client = Client()
        cls.author_user_client.force_login(cls.author)

        cls.not_author_user_client = Client()
        cls.not_author_user_client.force_login(cls.not_author_user)


class TestContent(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.list_url = reverse('notes:list')
        cls.detail_url = reverse(
            'notes:detail',
            kwargs={'slug': cls.note.slug}
        )

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
        }

    def test_note_in_list_for_author(self):
        response = self.author_user_client.get(
            self.urls_list['notes:list']
        )
        context_objects = response.context['object_list']
        self.assertIn(self.note, context_objects)

    def test_note_not_in_list_for_another_user(self):
        response = self.not_author_user_client.get(
            self.urls_list['notes:list']
        )
        context_objects = response.context['object_list']
        self.assertNotIn(self.note, context_objects)

    def test_edit_create_pages_contains_form(self):
        urls = ('notes:add', 'notes:edit')
        for name in urls:
            with self.subTest(name=name):
                url = self.urls_list['notes:edit']
                response = self.author_user_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
