from django.shortcuts import redirect, render

from .models import Article
from .forms import ArticleForm

# Create your views here.
def index(request):
    """
    [메인 페이지]
    - 메인 페이지에는 전체 게시글 목록이 출력됨
    - 따라서 DB에서 전체 게시글을 가져와야 함
    - CRUD 중 READ : 전체 게시글 조회
    """
    # 1. DB에서 전체 게시글 조회
    #    - Article.objects.all() 의 결과는 QuerySet (게시글 객체들의 묶음)
    articles = Article.objects.all()

    # 2. 템플릿에 넘겨줄 데이터를 딕셔너리로 묶기
    #    - key('articles') => 템플릿에서 사용할 변수 이름
    #    - value(articles) => 실제로 전달되는 데이터
    context = {
        'articles': articles,
    }

    # 3. 템플릿(index.html)에 데이터(context)를 채워 HTML을 만들고, 응답으로 반환
    return render(request, 'articles/index.html', context)


def detail(request, article_pk):
    """
    [단일 게시글 조회]
    - URL에서 넘겨받은 article_pk로 몇 번 게시글을 볼지 결정
    - DB에서 해당 게시글 1개를 조회한 뒤 템플릿에 전달
    - CRUD 중 READ : 단일 게시글 조회
    """
    # 1. pk가 article_pk인 게시글 1개 조회
    #    - get()의 결과는 QuerySet이 아닌 Article 객체 1개
    article = Article.objects.get(pk=article_pk)

    # 2. 템플릿에 넘겨줄 데이터를 딕셔너리로 묶기
    context = {
        'article': article,
    }

    # 3. 템플릿(detail.html)에 데이터를 채워 HTML을 만들고, 응답으로 반환
    return render(request, 'articles/detail.html', context)


# def new(request):
#     """
#     [게시글 작성 페이지] - create와 한 쌍 (GET)
#     - 제목/내용을 입력할 form이 담긴 빈 페이지를 응답
#     - DB 작업 없음 (아직 저장할 데이터가 없으므로)
#     """
#     # 1. ArticleForm 클래스로 인스턴스를 생성
#     form = ArticleForm()

#     # 2. context 데이터 준비
#     context = {
#         'form': form,
#     }

#     return render(request, 'articles/new.html', context)


# def create(request):
#     """
#     [게시글 저장] - new와 한 쌍 (POST)
#     - new 페이지의 form에서 제출된 데이터를 받아 DB에 저장
#     - CRUD 중 CREATE
#     """
#     # 1. form에서 제출된 제목과 내용 꺼내기
#     #    - request.POST : form 데이터가 담긴 딕셔너리 형태의 객체
#     #    - get('title') 의 'title' => input 태그의 name 속성 값
#     title = request.POST.get('title')
#     content = request.POST.get('content')

#     # 2. Article 인스턴스 생성 후 DB에 저장
#     #    - 인스턴스를 만든 것만으로는 저장되지 않음, save()를 호출해야 저장됨
#     article = Article(title=title, content=content)
#     article.save()

#     # (사용하지 않는 방식) 저장 완료 페이지를 바로 render로 응답
#     # => 이 화면에서 새로고침하면 POST 요청이 다시 전송되어 같은 글이 중복 저장됨
#     # return render(request, 'articles/create.html')

#     # 3. 방금 저장한 게시글의 상세 페이지로 redirect
#     #    - 서버가 브라우저에게 "이 주소로 다시 요청해"라고 지시하는 응답
#     #    - redirect('app_name:URL name', URL에 들어갈 값)
#     #    - article.pk는 save() 이후에 생성되므로 이 시점에 사용 가능
#     return redirect('articles:detail', article.pk)

# def create(request):
#     # 1. ArticleForm 인스턴스 생성 + 사용자 입력 데이터까지 받아서 
#     # 모델 폼이기 때문에 데이터를 통째로 받아도 모델 필드 매칭을 진행 할 수 있음
#     # form = ArticleForm(data=request.POST)
#     form = ArticleForm(request.POST)

#     # 2. 저장 전에 "유효성 검사"
#     # 모델 폼 인스턴스의 is_valid() 인스턴스 메서드가 유효성 검사를 진행
#     if form.is_valid():
#         # 3.1 유효성 검사를 통과했다면 저장
#         # save 메서드는 저장하여 생성된 객체를 반환해줌
#         article = form.save()
#         # 3.2 저장 후에 어디론가 리다이렉트
#         return redirect('articles:detail', article.pk)
#     context = {
#         'form': form,
#     }
#     # 4. 통과하지 못했다면, new 페이지를 에러메세지와 함께 응답
#     return render(request, 'articles/new.html', context)

# 완성된 create 코드
def create(request):
    # 1. 만약 요청 메서드가 POST라면 (create 로직)
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save()
            return redirect('articles:detail', article.pk)
    # 2. 만약 요청 메서드가 POST가 아니라면 (new 로직)
    # 왜 굳이 if에서 POST만 단독으로 확인을 하는지
    # 사실 요청 메서드는 GET/POST말고 다른 메서드들이 존재합니다.
    # 지금 이 view함수에서 가장 중요한 로직은 DB와 소통하는 부분
    # 즉, POST일때만 확실하게 해야하는 중요한 일을 먼저 확인하고,
    # 나머지 일(페이지 리턴)은 사실 GET/PUT/DELETE건 크게 중요하지 않은 일
    # 혹시나 클라이언트가 POST가 아닌 다른 메서드로 요청을 보내더라도 단순히 페이지를 응답하는 로직이 돌아갈 수 있도록 하기 위함
    else:
        form = ArticleForm()
    context = {
        'form': form,
    }
    return render(request, 'articles/new.html', context)


def delete(request, article_pk):
    """
    [게시글 삭제]
    - 삭제할 게시글을 먼저 조회한 뒤 삭제
    - CRUD 중 DELETE
    """
    # 1. 삭제할 게시글 조회
    article = Article.objects.get(pk=article_pk)

    # 2. DB에서 삭제
    article.delete()

    # 3. 삭제된 글의 상세 페이지는 더 이상 없으므로 메인 페이지로 redirect
    return redirect('articles:index')


# def edit(request, article_pk):
#     """
#     [게시글 수정 페이지] - update와 한 쌍 (GET)
#     - 기존 제목/내용이 미리 채워진 form 페이지를 응답
#     """
#     # 1. 수정할 게시글 조회
#     #    - 기존 값을 form의 value에 채워두기 위해 필요
#     article = Article.objects.get(pk=article_pk)

#     # 2. 모델 폼 ArticleForm 인스턴스를 생성 (+ 기존 데이터)
#     form = ArticleForm(instance=article)

#     # 2. 템플릿에 넘겨줄 데이터를 딕셔너리로 묶기
#     context = {
#         'article': article,
#         'form': form,
#     }

#     # 3. 템플릿(edit.html)에 데이터를 채워 HTML을 만들고, 응답으로 반환
#     return render(request, 'articles/edit.html', context)


# def update(request, article_pk):
#     """
#     [게시글 수정 저장] - edit과 한 쌍 (POST)
#     - edit 페이지의 form에서 제출된 데이터로 기존 게시글을 갱신
#     - CRUD 중 UPDATE
#     """
#     # 1. 수정할 게시글 조회
#     article = Article.objects.get(pk=article_pk)

#     # 2. form에서 제출된 값으로 객체의 속성 덮어쓰기
#     #    - 아직 DB에는 반영되지 않은 상태
#     article.title = request.POST.get('title')
#     article.content = request.POST.get('content')

#     # 3. DB에 반영
#     #    - 이미 pk가 있는 객체 => save()가 새로 만들지 않고 기존 데이터를 갱신
#     article.save()

#     # 4. 수정한 게시글의 상세 페이지로 redirect
#     return redirect('articles:detail', article.pk)

# def update(request, article_pk):
#     # 1. 수정할 게시글 조회
#     article = Article.objects.get(pk=article_pk)

#     # 2. 사용자 입력데이터 (+ 수정이기 때문에 기존 데이터도 함께 포함)를 모델 폼으로 받음
#     form = ArticleForm(request.POST, instance=article)

#     # 3. 유효성 검사
#     if form.is_valid():
#         # form 객체가 기존 데이터를 가지고 있기 때문에 save는 생성이 아닌 갱신을 진행
#         form.save()
#         return redirect('articles:detail', article.pk)
#     context = {
#         'article': article,
#         'form': form,
#     }
#     return render(request, 'articles/edit.html', context)

# 완성된 update 코드
def update(request, article_pk):
    article = Article.objects.get(pk=article_pk)
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            return redirect('articles:detail', article.pk)
    else:
        form = ArticleForm(instance=article)
    context = {
        'article': article,
        'form': form,
    }
    return render(request, 'articles/edit.html', context)