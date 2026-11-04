from django.urls import path
from . import views


app_name = 'books'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:book_pk>', views.detail, name='detail'),
    path('create', views.create, name='create'),
    path('<int:book_pk>/delete', views.delete, name='delete'),
    path('<int:book_pk>/update', views.update, name='update'),
]
