import shutil

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.forms import PostForm
from posts.models import Post, Group
from . import advanced_value as av

User = get_user_model()


class PostFormTests(TestCase):
    group = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title=av.GROUP_TITLE,
            slug=av.GROUP_SLUG,
            description=av.GROUP_DESCRIPTION)

        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(av.MEDIA_TEMP, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(username=av.AUTHOR,
                                             password=av.PASSWORD)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            text=av.POST_TEXT,
            pub_date=av.POST_DATE,
            group=PostFormTests.group,
            author=self.user
        )
        self.post_url = f'/{self.user.username}/{self.post.id}/'

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=av.GIF_IMG,
            content_type='image/gif'
        )
        form_data = {
            'text': av.POST_TEXT,
            'author': self.post.author,
            'group': self.post.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            av.POST_NEW,
            data=form_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=av.POST_TEXT,
                image='posts/small.gif'
            ).exists()
        )
        self.assertRedirects(response, av.INDEX_URL)

    def test_redirect_update_post(self):
        """После радактирования юзер перенаправлен на страницу поста."""
        form = {
            'text': f'testiki {av.POST_TEXT}',
            'author': self.post.author,
            'group': self.post.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'username': self.post.author,
                            'post_id': self.post.group.id}),
            data=form
        )
        self.assertRedirects(response, self.post_url)
