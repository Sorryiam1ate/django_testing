from notes.tests.conftest import BaseTestCase
from notes.forms import NoteForm


class TestContent(BaseTestCase):

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
                url = self.urls_list[name]
                response = self.author_user_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
