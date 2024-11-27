from django.contrib.auth.models import User
from django.urls import reverse
from django.test import Client, TestCase

from notes.models import Note


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создание авторов
        cls.author = User.objects.create(username='testuser')
        cls.not_author_user = User.objects.create(username='not_author_user')

        # Настройка клиентов
        cls.author_user_client = Client()
        cls.author_user_client.force_login(cls.author)

        cls.not_author_user_client = Client()
        cls.not_author_user_client.force_login(cls.not_author_user)

        # Создание тестовой заметки
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

        # Список маршрутов
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
