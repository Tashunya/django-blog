from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.postgres.search import TrigramSimilarity
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count

from taggit.models import Tag
from .models import Post, Comment
from .forms import PostForm, CommentForm, SearchForm


def post_list(request, tag_slug=None):
    object_list = Post.published_posts.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3)  # 3 posts per page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post_list.html', {'page': page, 'posts': posts, 'tag': tag})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # all tags of current post
    post_tags_ids = post.tags.values_list('id', flat=True)
    # all posts with at least one tag of post_tags_ids excluding current post
    similar_posts = Post.published_posts.filter(tags__in=post_tags_ids).exclude(id=post.id)
    # count number of same tags, sort list and slice first 4 posts
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).\
        order_by('-same_tags', '-published_date')[:4]
    return render(request, 'blog/post_detail.html',
                  {'post': post,
                   'similar_posts': similar_posts})


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']

            # weight: A = 1 B = 0.4 C = 0.2 D = 0.1
            # search_vector = SearchVector('title', weight='A') + SearchVector('text', weight='B')
            # search_query = SearchQuery(query)

            # Using field ranks (>= 0.3)
            # results = Post.objects.annotate(
            #     search=search_vector, rank=SearchRank(search_vector, search_query)).\
            #     filter(rank__gte=0.3).order_by('-rank')

            # Using trigram
            # results = Post.objects.annotate(
            #     similarity=TrigramSimilarity('title', query),
            # ).filter(similarity__gt=0.3).order_by('-similarity')

    return render(request, 'blog/post/search.html', {'form': form,
                                                     'query': query,
                                                     'results': results})


@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            messages.success(request, 'Запись создана')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        messages.info(request, 'You can\'t do that')
        return redirect('post_list')
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            messages.success(request, 'Запись изменена')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})


@login_required
def post_draft_list(request):
    posts = Post.draft_posts.filter(author=request.user)
    return render(request, 'blog/post_draft_list.html', {'posts': posts})


@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user == post.author:
        post.publish()
        messages.success(request, 'Запись опубликована')
        return redirect('post_detail', pk=pk)
    else:
        messages.info(request, 'You can\'t do that!')
        return redirect('post_detail', pk=pk)


@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user == post.author:
        post.delete()
        messages.success(request, 'Запись удалена')
        return redirect('post_list')
    else:
        messages.info(request, 'You can\'t do that!')
        return redirect('post_detail', pk=pk)


def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.post.author == request.user:
        comment.approve()
        return redirect('post_detail', pk=comment.post.pk)
    else:
        messages.info(request, 'You can\'t do that!')
        return redirect('post_detail', pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.post.author == request.user:
        comment.delete()
        return redirect('post_detail', pk=comment.post.pk)
    else:
        messages.info(request, 'You can\'t do that!')
        return redirect('post_detail', pk=comment.post.pk)
