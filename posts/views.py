from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator

from yatube.settings import COUNT_PAGE
from .forms import PostForm, CommentForm
from .models import Group, Post, User, Comment, Follow


def pagination_page(request, post_list=None, pages=COUNT_PAGE):
    """Определяет кол-во страниц и записей на них."""
    if post_list is None:
        post_list = {}
    paginator = Paginator(post_list, pages)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    post_list = pagination_page(request, Post.objects.all())
    return render(request, 'index.html', {'page': post_list, 'index': True})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = pagination_page(request, Post.objects.filter(group=group))
    return render(request, 'group.html',
                  {'group': group, 'page': post_list})


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=user)
    user_following = Follow.objects.filter(author_id=user.id).values_list(
        'author_id', flat=True).count()
    following = Follow.objects.filter(
        user_id=request.user.id, author_id=user.id).count()
    follow = Follow.objects.filter(user_id=user.id).count()
    context = {
        'author': user,
        'count_posts': post_list.count(),
        'page': pagination_page(request, post_list),
        'following': following,
        'follow': follow,
        'user_following': user_following}
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=user)
    comment_list = Comment.objects.filter(post=post_id)
    post = Post.objects.get(pk=post_id)
    context = {
        'author': post.author,
        'text': post,
        'post_id': post.id,
        'comment_list': comment_list,
        'count_posts': post_list.count()}
    return render(request, 'post.html', context)


@login_required
def post_new(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form and form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('posts:index')
    return render(
        request, 'post_new.html',
        {'form': form, 'title': 'Добавить', 'button': 'Добавить'})


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if post.author != request.user:
        return redirect('posts:post', username=username, post_id=post_id)
    if form and form.is_valid():
        post = form.save(commit=False)
        post.save()
        return redirect('posts:post', username=username, post_id=post_id)
    return render(
        request, 'post_new.html', {'form': form, 'post': post,
                                   'title': 'Редактировать',
                                   'button': 'Сохранить'})


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form and form.is_valid():
        form.instance.author = request.user
        form.instance.post = post
        form.save()
        return redirect('posts:post', username=username, post_id=post_id)
    return render(request, 'comments.html', {'form': form})


@login_required
def follow_index(request):
    """Посты авторов на которых подписан пользователь."""
    authors = Follow.objects.filter(user_id=request.user.id).values_list(
        'author_id', flat=True)
    username = User.objects.filter(id__in=authors)
    post_list = pagination_page(request, Post.objects.filter(
        author__in=username))
    return render(request, 'follow.html', {'page': post_list, 'follow': True})


@login_required
def profile_follow(request, username):
    """Подписка на интересного автора."""
    user = get_object_or_404(User, username=username)
    following = Follow.objects.filter(
        user_id=request.user.id, author_id=user.id).count()
    if request.user.id != user.id and following < 1:
        follow = Follow(user=request.user, author=user)
        follow.save()
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    user = get_object_or_404(User, username=username)
    Follow.objects.filter(user_id=request.user.id, author_id=user.id).delete()
    return redirect('posts:follow_index')
