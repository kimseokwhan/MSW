from django.urls import path
from . import views

app_name = 'recommend'
urlpatterns = [
    path('', views.recommend_form, name='form'),            # 입력값 검증 및 저장
    path('text/', views.text_recommend, name='text'),       # 도서 추천 생성
    path('route/', views.decide_route, name='route'),       # 텍스트 또는 이미지 처리 경로 결정
    path('image/', views.image_recommend, name='image'),    # 표지 이미지 생성
    path('analyze/', views.image_analysis, name='analyze'), # 책 표지 분석
    path('flow/', views.recommend_flow, name='flow'),       # 경로 결정부터 결과 출력까지 처리
]
