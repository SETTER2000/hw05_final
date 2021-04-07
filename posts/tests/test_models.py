from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Post, Group
from . import advanced_value as av

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.post = Post.objects.create(
            text=av.POST_TEXT,
            pub_date=av.POST_DATE,
            author=User.objects.create(
                username=av.POST_DATE,
                password=av.PASSWORD),
            group=Group.objects.create(
                title=av.GROUP_TITLE,
                slug=av.GROUP_SLUG,
                description=av.GROUP_DESCRIPTION)
        )

    def test_verbose_name(self):
        """verbose_name в полях объекта Post совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'сообщение',
            'author': 'автор',
            'group': 'группа',
            'pub_date': 'дата публикации',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Напишите, что вы думаете по этой теме.',
            'author': 'Пользователь оставивший сообщение.',
            'group': 'Группа сообщений.',
            'pub_date': 'Дата публикации сообщения на сайте.',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_object_name_is_title_fild(self):
        """В поле __str__  объекта post записано значение поля post.text."""
        post = PostModelTest.post
        expected_object_text = post.text
        self.assertEqual(expected_object_text, str(post.text))


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title=av.GROUP_TITLE,
            slug=av.GROUP_SLUG,
            description=av.GROUP_DESCRIPTION
        )

    def test_verbose_name(self):
        """verbose_name в полях объекта Group совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_verboses = {
            'title': 'название группы',
            'slug': 'url group',
            'description': 'описание'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_object_name_is_title_fild(self):
        """В поле __str__  объекта group записано значение поля title."""
        group = GroupModelTest.group
        expected_object_text = group.title
        self.assertEqual(expected_object_text, str(group))
