from django.urls import path
from libraries import views

urlpatterns = [
    path('libraries/', views.library_list),
    path('libraries/<int:library_pk>/', views.library_detail),
]
