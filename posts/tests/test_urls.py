from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post
from . import advanced_value as av

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title=av.GROUP_TITLE,
            description=av.GROUP_DESCRIPTION,
            slug=av.GROUP_SLUG
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username=av.AUTHOR,
                                             password=av.PASSWORD)
        self.user2 = User.objects.create_user(username=av.AUTHOR2,
                                              password=av.PASSWORD)
        self.authorized_client = Client()
        self.authorized_client_not_author = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_not_author.force_login(self.user2)

        self.post = Post.objects.create(
            text=av.GROUP_DESCRIPTION,
            pub_date=av.POST_DATE,
            author=self.user,
            group=PostURLTests.group
        )
        self.profile_url = f'/{self.user.username}/'
        self.post_url = f'/{self.user.username}/{self.post.id}/'
        self.post_edit = f'/{self.user.username}/{self.post.id}/edit/'

    def test_page_accessible_not_authorized_user(self):
        """Страницы доступны любому пользователю."""
        url_exists = [av.INDEX_URL, av.GROUP_URL, av.ABOUT_AUTHOR,
                      av.ABOUT_TECH]
        for link in url_exists:
            with self.subTest():
                response = self.guest_client.get(link)
                self.assertEqual(response.status_code, 200)

    def test_page_accessible_authorized_user(self):
        """Страницы доступны авторизованному пользователю."""
        url_authorized_user = [av.POST_NEW, self.post_edit]
        for link in url_authorized_user:
            with self.subTest():
                response = self.authorized_client.get(link)
                self.assertEqual(response.status_code, 200)

    def test_page_exists_authorized_client_stranger_post(self):
        """Нет доступа к странице редактирования поста для
        авторизованного пользователя — не автора этого поста.
        """
        urls = [self.post_edit]
        for link in urls:
            with self.subTest():
                response = self.authorized_client_not_author.get(link)
                self.assertEqual(response.status_code, 302)
                self.assertRedirects(response, self.post_url)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            av.INDEX_TPL: av.INDEX_URL,
            av.GROUP_TPL: av.GROUP_URL,
            av.ABOUT_TECH_TPL: av.ABOUT_TECH,
            av.ABOUT_AUTHOR_TPL: av.ABOUT_AUTHOR,
            av.PROFILE_TPL: self.profile_url,
            av.POST_TPL: self.post_url,

        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_url_post_new_template(self):
        """URL-адреса используют один и тот же шаблон."""
        urls = [self.post_edit,
                av.POST_NEW]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, av.POST_NEW_TPL)

    def test_redirect_to_page_post(self):
        """Редирект пользователя на страницу поста с правильным шаблоном."""
        urls = [self.post_edit]
        for url in urls:
            with self.subTest():
                response = self.authorized_client_not_author.get(url).url
                response = self.authorized_client_not_author.get(response)
                self.assertTemplateUsed(response, av.POST_TPL)
