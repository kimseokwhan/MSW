from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    GENDER_CHOICES = [('M', '남성'), ('F', '여성'), ('O', '기타')]
    email = models.EmailField(verbose_name='이메일', blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, verbose_name='성별')
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name='나이')
    weekly_reading_time = models.PositiveIntegerField(default=0, verbose_name='주간 평균 독서 시간(분)')
    yearly_reading_amount = models.PositiveIntegerField(default=0, verbose_name='연간 독서량(권)')
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name='프로필 사진')
    followings = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)
    favorite_categories = models.ManyToManyField('books.Category', related_name='interested_users', blank=True)
    
    def __str__(self):
        return self.username