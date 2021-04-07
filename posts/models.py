import textwrap

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Сообщество."""
    title = models.CharField(
        'название группы',
        max_length=200,
        help_text='Придумайте краткое и ёмкое название для группы сообщений')
    slug = models.SlugField(
        unique=True,
        max_length=100,
        verbose_name='url group',
        help_text='Краткое, уникальное слово, которое будет '
                  'видно в ссылке на страницу группы (часть URL)')
    description = models.TextField(
        'описание',
        help_text='Опишите группу так, чтобы пользователь мог легко  '
                  'определиться с выбором группы для сообщения.')

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'posts_group'
        verbose_name = 'group'
        verbose_name_plural = 'Группа'


class Post(models.Model):
    """Публикация пользователя."""

    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    text = models.TextField(
        'сообщение',
        default='ваш текст',
        help_text='Напишите, что вы думаете по этой теме.')
    pub_date = models.DateTimeField(
        'дата публикации',
        auto_now_add=True,
        help_text='Дата публикации сообщения на сайте.',
        db_index=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
        help_text='Пользователь оставивший сообщение.',
        related_name='author_posts')
    group = models.ForeignKey(
        'Group',
        models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='группа',
        help_text='Группа сообщений.',
        related_name='group_posts')

    def __str__(self):
        return [f'author: {self.author}, '
                f'group: {self.group}, '
                f'pub_date: {self.pub_date}, '
                f'text: {textwrap.wrap(self.text[:15])}']

    class Meta:
        db_table = 'posts_post'
        ordering = ('-pub_date',)
        verbose_name = 'post'
        verbose_name_plural = 'сообщения'


class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        verbose_name='пост',
        help_text='Сообщение.',
        related_name='comment_post')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
        help_text='Пользователь оставивший комментарий.',
        related_name='author_comment')
    text = models.TextField(
        'комментарий',
        default='ваш текст',
        help_text='Напишите, что вы думаете по этой теме.')
    created = models.DateTimeField(
        'дата и время публикации',
        auto_now_add=True,
        help_text='дата и время публикации комментария на сайте.')


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
        help_text='Пользователь, который подписывается.',
        related_name='following')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='пост',
        help_text='Пользователь, на которого подписываются.',
        related_name='follower')
