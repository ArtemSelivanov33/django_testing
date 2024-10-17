
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username='user1',
            password='password1'
        )
        cls.user2 = User.objects.create_user(
            username='user2',
            password='password2'
        )
        cls.slug = 'my-note'

    def login_as_user1(self):
        self.client.login(
            username='user1',
            password='password1'
        )

    def test_user_can_create_note(self):
        """Создание заметки залогиненным пользователем."""
        self.login_as_user1()
        self.client.post(
            reverse(
                'notes:add'
            ),
            {
                'title': 'Заметка пользователя 1',
                'text': 'Содержимое заметки',
                'slug': self.slug
            }
        )
        self.assertEqual(
            Note.objects.count(),
            1
        )
        self.assertEqual(
            Note.objects.get().title,
            'Заметка пользователя 1'
        )

    def test_anonymous_user_cannot_create_note(self):
        """Тест,что анонимный пользователь не может создать заметку."""
        self.client.post(
            reverse(
                'notes:add'
            ),
            {
                'title': 'Заметка',
                'text': 'Содержимое заметки',
                'slug': 'my-note'
            }
        )
        self.assertEqual(
            Note.objects.count(),
            0
        )

    def test_cannot_create_note_with_duplicate_slug(self):
        """Тест,что невозможно создать две заметки с одинаковым slug."""
        self.login_as_user1()
        self.client.post(
            reverse(
                'notes:add'
            ),
            {
                'title': 'Первая заметка',
                'text': 'Содержимое первой заметки',
                'slug': self.slug
            }
        )
        response = self.client.post(reverse('notes:add'), {
            'title': 'Вторая заметка',
            'text': 'Содержимое второй заметки',
            'slug': self.slug
        })
        self.assertEqual(
            Note.objects.count(),
            1
        )
        self.assertFormError(
            response,
            'form',
            'slug',
            f'{self.slug}{WARNING}'
        )

    def test_slug_is_generated_if_empty(self):
        """Проверка автоматического создания slug."""
        self.login_as_user1()
        self.client.post(reverse('notes:add'), {
            'title': 'Заметка без slug',
            'text': 'Содержимое заметки'
        })
        note = Note.objects.get(
            title='Заметка без slug'
        )
        self.assertTrue(note.slug)
        self.assertEqual(
            note.slug,
            slugify('Заметка без slug')
        )

    def test_user_can_edit_own_note(self):
        """Пользователь может редактировать свои заметки."""
        self.login_as_user1()
        note = Note.objects.create(
            title='Заметка',
            text='Содержимое',
            author=self.user1
        )
        self.client.post(
            reverse(
                'notes:edit',
                args=[note.slug]), {
                'title': 'Отредактированная заметка',
                'text': 'Новое содержимое',
                'slug': note.slug
            }
        )
        note.refresh_from_db()
        self.assertEqual(
            note.title,
            'Отредактированная заметка'
        )

    def test_user_cannot_edit_other_user_note(self):
        """Пользователь не может редактировать заметки других поль-лей."""
        self.login_as_user1()
        note = Note.objects.create(
            title='Заметка',
            text='Содержимое',
            author=self.user2
        )
        self.client.post(
            reverse(
                'notes:edit',
                args=[note.slug]), {
                'title': 'Попытка редактирования чужой заметки',
                'text': 'Содержимое',
                'slug': note.slug
            }
        )
        note.refresh_from_db()
        self.assertEqual(
            note.title,
            'Заметка'
        )

    def test_user_can_delete_own_note(self):
        """Пользователь может удалить свои заметки."""
        self.login_as_user1()
        note = Note.objects.create(
            title='Удаляемая заметка',
            text='Содержимое',
            author=self.user1
        )
        self.client.post(
            reverse(
                'notes:delete',
                args=[note.slug]
            )
        )
        self.assertEqual(
            Note.objects.count(),
            0
        )

    def test_user_cannot_delete_other_user_note(self):
        """Пользователь не может удалить заметки других пользователей."""
        self.login_as_user1()
        note = Note.objects.create(
            title='Заметка',
            text='Содержимое',
            author=self.user2
        )
        self.client.post(
            reverse(
                'notes:delete',
                args=[note.slug]
            )
        )
        self.assertEqual(
            Note.objects.count(),
            1
        )
