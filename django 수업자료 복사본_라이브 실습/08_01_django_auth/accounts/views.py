from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login

# Create your views here.

# 로그인은 세션을 Create하는 로직이다.
def login(request):
    # 1. POST 요청일 때 세션을 생성(+인증)
    
    if request.method == 'POST':
        # POST에 담겨진 사용자 입력 데이터를 받음
        # AuthenticationForm의 부모 클래스인 Form의 생성자 함수 인자 구성의 첫번째 인자는 request 다.
        form = AuthenticationForm(request, request.POST)
        # 유효성 검사
        if form.is_valid():
            # 세션 데이터를 생성 (login 빌트인 함수)
            # auth_login(요청 객체, 인증된 유저 객체)
            # AuthenticationForm이 제공하는 인스턴스 메서드 get user 메서드가 인증된 유저 객체를 반환 해줌
            user = form.get_user()
            auth_login(request, user)
            return redirect('articles:index')
    # 2. POST 요청이 아닐 떄는 로그인 페이지를 응답
    else:
        form = AuthenticationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/login.html', context)