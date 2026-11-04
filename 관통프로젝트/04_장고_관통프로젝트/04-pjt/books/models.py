from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    review = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text='1점에서 10점 사이의 점수를 입력하세요'
    )
    author = models.CharField(max_length=100)