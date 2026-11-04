from django.shortcuts import render
from .models import Article

# Create your views here.
def index(request):
    """
    [메인페이지 응답]
    - 메인페이지에는 전체 게시슬 데이터가 출력됨
    - DB에서 전체 게시글을 가져와야 함
    - READ : 전체 게시글 조회
    """
    # 1. 전체 게시글 조회 요청 후 응답 결과를 변수에 할당
    articles = Article.objects.all()

    # 2. 응답 결과(전체 게시글 데이터)를 템플릿에서 출력할 수 있도록 준비
    context = {
        'articles': articles,
    }

    # 3. 메이 페이지(index.html)을 응답 데이터로 렌더링
    return render(request, 'articles/index.html', context)