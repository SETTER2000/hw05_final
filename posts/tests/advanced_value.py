import os
import tempfile

from django.urls import reverse
from django.conf import settings

AUTHOR = 'Clare'
AUTHOR2 = 'Adam'
GROUP_TITLE = 'Собачки'
INITIAL_TEXT = 'ваш текст'
PASSWORD = 'password'
GROUP_SLUG = 'dogs'
GROUP_DESCRIPTION = 'Собачки это вам ни кошечки.'
COUNT_OBJECTS = 13
POST_DATE = '2021-03-01 00:00:00'
POST_TEXT = 'Тестовый текст' * 5
ABOUT_AUTHOR = reverse('about:author')
ABOUT_TECH = reverse('about:tech')
POST_NEW = reverse('posts:post_new')
INDEX_URL = reverse('posts:index')
GROUP_URL = reverse('posts:group_posts', kwargs={'slug': GROUP_SLUG})
ADD_COMMENT_URL = reverse('posts:add_comment',
                          kwargs={'username': AUTHOR, 'post_id': 1})
FOLLOWING_URL = reverse('posts:profile_follow', kwargs={'username': AUTHOR})
UN_FOLLOWING_URL = reverse('posts:profile_unfollow',
                           kwargs={'username': AUTHOR})
FOLLOW_URL = reverse('posts:follow_index')
INDEX_TPL = 'index.html'
GROUP_TPL = 'group.html'
ABOUT_TECH_TPL = 'about/tech.html'
ABOUT_AUTHOR_TPL = 'about/author.html'
PROFILE_TPL = 'profile.html'
POST_TPL = 'post.html'
POST_NEW_TPL = 'post_new.html'
GIF_IMG = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
MEDIA_TEMP = settings.MEDIA_ROOT = tempfile.mkdtemp(
    dir=os.path.join(settings.BASE_DIR, 'media'))
