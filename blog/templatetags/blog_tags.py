from django import template
from django.db.models import Count
from ..models import Post, Comment

register = template.Library()


@register.simple_tag
def total_posts(user):
    #return Post.published_posts.count()
    return Post.published_posts.filter(author=user).count()


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published_posts.order_by("-published_date")[:count]
    return {'latest_posts': latest_posts}


@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published_posts.annotate(total_comments=Count('comments')).\
        filter(total_comments__gt=0).order_by('-total_comments')[:count]
