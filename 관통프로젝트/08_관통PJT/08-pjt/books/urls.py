from django.urls import path
from . import views


urlpatterns = [
    path('books/', views.book_list),
    path('books/<int:book_pk>/', views.book_detail),
]
