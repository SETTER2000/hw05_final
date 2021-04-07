from itertools import islice
import shutil
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import SimpleTestCase, override_settings
from django.urls import path, reverse
from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import caches
from yatube.settings import COUNT_PAGE
from posts.models import Post, Group
from . import advanced_value as av

User = get_user_model()


def response_error_handler(request, exception=None):
    return HttpResponse('Error handler content', status=403)


def permission_denied_view(request):
    raise PermissionDenied


urlpatterns = [
    path('403/', permission_denied_view),
]

handler403 = response_error_handler


@override_settings(ROOT_URLCONF=__name__)
class CustomErrorHandlerTests(SimpleTestCase):
    def test_handler_renders_template_response(self):
        response = self.client.get('/403/')
        self.assertContains(response, 'Error handler content', status_code=403)


class PostPagesTests(TestCase):
    user2 = None
    count_object = None
    user = None
    group = None
    cache_name = 'index_page'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=av.AUTHOR,
                                            password=av.PASSWORD)
        cls.user2 = User.objects.create_user(username=av.AUTHOR2,
                                             password=av.PASSWORD)
        cls.group = Group.objects.create(
            title=av.GROUP_TITLE,
            slug=av.GROUP_SLUG,
            description=av.GROUP_DESCRIPTION)
        objs = (Post(
            text='Тестовый текст Tests',
            author=PostPagesTests.user,
            group=PostPagesTests.group,
            image=SimpleUploadedFile(
                name=f'small{ind}.gif',
                content=av.GIF_IMG,
                content_type='image/gif'
            )
        ) for ind in range(av.COUNT_OBJECTS))

        while True:
            batch = list(islice(objs, av.COUNT_OBJECTS))
            if not batch:
                break
            Post.objects.bulk_create(batch, av.COUNT_OBJECTS)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(av.MEDIA_TEMP, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client2 = Client()
        self.authorized_client.force_login(PostPagesTests.user)
        self.authorized_client2.force_login(PostPagesTests.user2)
        self.post = Post.objects.get(pk=1)
        self.profile_url = f'/{self.user.username}/'
        self.post_url = f'/{self.user.username}/{self.post.id}/'
        self.post_edit = f'/{self.user.username}/{self.post.id}/edit/'

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            av.INDEX_TPL: av.INDEX_URL,
            av.POST_NEW_TPL: av.POST_NEW,
            av.GROUP_TPL: av.GROUP_URL
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_shows_correct_context(self):
        """На страницу home передаётся ожидаемое количество объектов."""
        response = self.authorized_client.get(av.INDEX_URL)
        self.assertEqual(len(response.context['page']), COUNT_PAGE)

    def test_first_page_containse_ten_records(self):
        """Pagination. Первая стр. 10 объектов."""
        response = self.authorized_client.get(av.INDEX_URL)
        self.assertEqual(len(response.context.get('page').object_list),
                         COUNT_PAGE)

    def test_second_page_containse_three_records(self):
        """Pagination. Вторая стр. 3 объекта."""
        response = self.authorized_client.get(
            av.INDEX_URL + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)

    def test_post_new_shows_correct_context(self):
        """Шаблон post_new сформирован с правильными полями формы."""
        response = self.authorized_client.get(av.POST_NEW)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_initial_value(self):
        """Предустановленнное значение формы для стр. /new."""
        response = self.authorized_client.get(av.POST_NEW)
        text_obj = response.context['form'].fields['text'].initial
        self.assertEqual(text_obj, av.INITIAL_TEXT)

    def test_post_page_index_and_group_posts_correct_context(self):
        """Словарь context.posts, коррелирует на разных страницах."""
        post = Post.objects.create(
            text='Тестовый текст Tests',
            author=PostPagesTests.user,
            group=PostPagesTests.group,
            image=SimpleUploadedFile(
                name=f'small.gif',
                content=av.GIF_IMG,
                content_type='image/gif'
            ))

        form_fields = [av.INDEX_URL, av.GROUP_URL, self.profile_url]
        for value in form_fields:
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                post_context = response.context['page'][0]
                self.assertEqual(
                    post_context.author.username, post.author.username)
                self.assertEqual(post_context.text, post.text)
                self.assertEqual(post_context.image, post.image)

    def test_post_list_page_group_correct_context(self):
        """Словарь context.group, для страницы group соответствует."""
        response = self.authorized_client.get(av.GROUP_URL)
        object_group = response.context['group']
        self.assertEqual(object_group.description, av.GROUP_DESCRIPTION)
        self.assertEqual(object_group.title, av.GROUP_TITLE)
        self.assertEqual(object_group.slug, av.GROUP_SLUG)

    def test_post_edit_correct_context(self):
        """Словарь context, для страницы редактирования поста
        соответствует."""
        response = self.authorized_client.get(self.post_edit)
        group = Post.objects.filter(pk=self.post.id)
        context = {
            self.post.text: response.context['form'].initial['text'],
            PostPagesTests.group.title: group[0].group.title
        }
        for value, expected in context.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_profile_correct_context(self):
        """Словарь context, для страницы профайла."""
        response = self.authorized_client.get(self.profile_url)
        context = {
            response.context['count_posts']: av.COUNT_OBJECTS,
            str(response.context['author']): PostPagesTests.user.username
        }
        for value, expected in context.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_post_correct_context(self):
        """Словарь context, для страницы поста."""
        response = self.authorized_client.get(self.post_url)
        self.assertIsInstance(response.context['text'], Post)
        context = {
            response.context['text'].text: self.post.text,
            response.context['count_posts']: av.COUNT_OBJECTS,
            str(response.context['author']): PostPagesTests.user.username,
            response.context["text"].image: self.post.image
        }
        for value, expected in context.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_cache_list_post_index_page(self):
        """Кэш для списка постов на главной"""
        post = Post.objects.create(
            text='КЭШ и КЫШ',
            author=PostPagesTests.user,
            group=PostPagesTests.group)
        response = self.authorized_client.get(av.INDEX_URL)
        self.assertEqual(post.text, response.context.get('page').object_list[0].text)

    def test_authorize_user_add_comment(self):
        """Только авторизированный пользователь может комментировать посты."""
        response = self.guest_client.get(av.ADD_COMMENT_URL)
        self.assertRedirects(response, f'/auth/login/?next={av.ADD_COMMENT_URL}')

    def test_authorize_user_add_del_following(self):
        """Авторизованный пользователь может подписываться на других пользователей и удалять их из подписок."""
        response = self.authorized_client.get(av.FOLLOWING_URL)
        self.assertRedirects(response, av.FOLLOW_URL)
        response = self.authorized_client.get(av.UN_FOLLOWING_URL)
        self.assertRedirects(response, av.FOLLOW_URL)

    def test_new_post_added_following(self):
        """Новая запись пользователя появляется в ленте тех, кто на него подписан и не появляется в ленте тех,
        кто не подписан на него."""
        post = Post.objects.create(
            text='Тестовый текст',
            author=PostPagesTests.user,
            group=PostPagesTests.group)
        response = self.authorized_client2.get(reverse('posts:profile_follow', kwargs={'username': av.AUTHOR}))
        self.assertRedirects(response, av.FOLLOW_URL)
        response = self.authorized_client2.get(av.FOLLOW_URL)
        self.assertEqual(post.text, response.context.get('page').object_list[0].text)
        response = self.authorized_client.get(av.FOLLOW_URL)
        if len(response.context.get('page').object_list) > 0:
            self.assertEqual(post.text, response.context.get('page').object_list[0].text)

