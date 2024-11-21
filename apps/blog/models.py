from django.contrib.postgres.fields import ArrayField
from django.db import models

from apps.accounts.models import CustomUser


# Create your models here.
class Post(models.Model):
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="posts"
    )
    title = models.CharField(max_length=500, verbose_name="Post title", unique=True)
    body = models.TextField()
    topics = ArrayField(models.CharField(max_length=50, default=str), default=list)
    post_slug = models.SlugField(allow_unicode=True, unique=True)
    liked_by = models.ManyToManyField(CustomUser, related_name="liked_posts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"`{self.title}` by {self.author.username}"

    class Meta:
        ordering = ("-created_at",)


class Comment(models.Model):
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="comments"
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    content = models.CharField(max_length=2000, verbose_name="Comment content")
    liked_by = models.ManyToManyField(CustomUser, related_name="liked_comments")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    edited = models.BooleanField(verbose_name="Edited comment", default=False)

    def __str__(self):
        return f"Commment `{self.content[0:15]}` by {self.author.username}"

    class Meta:
        ordering = ("-created_at",)


class Reply(models.Model):
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="replies"
    )
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="replies"
    )
    content = models.CharField()
    liked_by = models.ManyToManyField(CustomUser, related_name="liked_replies")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    edited = models.BooleanField(verbose_name="Edited reply", default=False)

    def __str__(self):
        return f"Reply `{self.content[0:15]}` by {self.author.username}"
