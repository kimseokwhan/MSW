from django.db import models
from django.conf import settings

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    
class Book(models.Model):
    title = models.CharField(max_length=200, verbose_name='도서 제목')
    description = models.TextField(verbose_name='도서 설명')
    review_score = models.FloatField(verbose_name='회원 리뷰 평점')
    author = models.CharField(max_length=100, verbose_name='저자')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='books')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='books')
    
    def __str__(self):
        return self.title


class Thread(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='threads')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='threads')
    title = models.CharField(max_length=200, verbose_name='쓰레드 제목')
    content = models.TextField(verbose_name='본문')
    reading_date = models.DateField(verbose_name='독서일')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_threads', blank=True)
    
    def __str__(self):
        return self.title


class Comment(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:30]