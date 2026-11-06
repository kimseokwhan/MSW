import base64
import requests
from django.conf import settings
from django.shortcuts import render
from .forms import RecommendationForm, ImageAnalysisForm

RECOMMEND_SYSTEM_PROMPT = '''
너는 친절한 도서 추천 도우미이다. 사용자의 취향과 상황에 맞는 책을 2~3권 추천하고,
각 책마다 제목, 저자, 추천 이유를 한두 문장으로 설명한다. 한국어로 답한다.
'''


def proxy_post(path, payload):
    """Proxy 연결 실패나 시간 초과를 안내 화면으로 처리한다."""
    try:
        return requests.post(settings.PROXY_URL + path, json=payload, timeout=180)
    except requests.RequestException:
        response = requests.Response()
        response.status_code = 503
        return response


# 입력값 검증 및 저장
def recommend_form(request):
    """입력값을 검증하고 저장한 내용을 보여준다."""
    saved = None
    if request.method == 'POST':
        form = RecommendationForm(request.POST)
        if form.is_valid():
            saved = form.save()
    else:
        form = RecommendationForm()
    context = {'title': '입력 검증', 'form': form, 'saved': saved}
    return render(request, 'recommend/input_form.html', context)


# 도서 추천 생성
def text_recommend(request):
    if request.method == 'POST':
        form = RecommendationForm(request.POST)
        if form.is_valid():
            result = form.save(commit=False)

            # 사용자 입력을 Proxy 서버에 보내 도서를 추천받는다.
            payload = {
                'messages': [
                    {'role': 'developer', 'content': RECOMMEND_SYSTEM_PROMPT},
                    {'role': 'user', 'content': result.request_text},
                ],
            }
            response = proxy_post('/chat/completions', payload)

            # 응답 코드에 따라 거절 또는 오류 화면을 보여준다.
            if response.status_code == 403:
                context = {'user_input': result.request_text}
                return render(request, 'recommend/rejected.html', context, status=403)
            if response.status_code != 200:
                context = {'user_input': result.request_text, 'status_code': response.status_code}
                return render(request, 'recommend/error.html', context, status=503)

            # 추천 결과를 저장하고 화면에 보여준다.
            data = response.json()
            result.content = data['content']

            result.save()
            context = {
                'title': '텍스트 추천 생성',
                'user_input': result.request_text,
                'result': result,
            }
            return render(request, 'recommend/result_text.html', context)
    else:
        form = RecommendationForm()
    context = {
        'title': '텍스트 추천 생성',
        'form': form,
    }
    return render(request, 'recommend/input_form.html', context)


# 텍스트 또는 이미지 처리 경로 결정
def decide_route(request):
    if request.method == 'POST':
        form = RecommendationForm(request.POST)
        if form.is_valid():
            result = form.save(commit=False)

            payload = {'prompt': result.request_text}
            response = proxy_post('/decide-route', payload)

            if response.status_code != 200:
                context = {'user_input': result.request_text, 'status_code': response.status_code}
                return render(request, 'recommend/error.html', context, status=503)

            data = response.json()
            result.route = data['route']
            result.content = f'결정된 route: {result.route}'
            result.save()
            context = {
                'title': '라우트 결정',
                'user_input': result.request_text,
                'result': result,
            }
            return render(request, 'recommend/result_text.html', context)
    else:
        form = RecommendationForm()
    context = {
        'title': '라우트 결정',
        'form': form,
    }
    return render(request, 'recommend/input_form.html', context)


# 표지 이미지 생성
def image_recommend(request):
    if request.method == 'POST':
        form = RecommendationForm(request.POST)
        if form.is_valid():
            result = form.save(commit=False)

            payload = {'prompt': result.request_text}
            response = proxy_post('/images/generations', payload)

            if response.status_code == 403:
                context = {'user_input': result.request_text}
                return render(request, 'recommend/rejected.html', context, status=403)
            if response.status_code != 200:
                context = {'user_input': result.request_text, 'status_code': response.status_code}
                return render(request, 'recommend/error.html', context, status=503)

            data = response.json()
            image_base64 = data['image_base64']                  # 생성된 JPEG 이미지 데이터

            result.save()
            context = {
                'title': '이미지 생성',
                'result': result,
                'image_base64': image_base64,      # 이미지를 HTML에 직접 넣어 표시한다.
            }
            return render(request, 'recommend/result_image.html', context)
    else:
        form = RecommendationForm()
    context = {
        'title': '이미지 생성',
        'form': form,
    }
    return render(request, 'recommend/input_form.html', context)


# 책 표지 분석
def image_analysis(request):
    if request.method == 'POST':
        form = ImageAnalysisForm(request.POST, request.FILES)
        if form.is_valid():
            result = form.save()                       # 업로드한 표지를 저장한다.

            # 표지 이미지를 API로 보낼 수 있게 base64로 변환한다.
            with result.image.open('rb') as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

            payload = {'image_base64': image_base64, 'question': result.question}
            response = proxy_post('/images/analysis', payload)

            if response.status_code == 403:
                context = {'user_input': result.question}
                return render(request, 'recommend/rejected.html', context, status=403)
            if response.status_code != 200:
                context = {'user_input': result.question, 'status_code': response.status_code}
                return render(request, 'recommend/error.html', context, status=503)

            data = response.json()
            result.content = data['content']
            result.save()
            context = {
                'title': '이미지 분석',
                'user_input': result.question,
                'result': result,
                'uploaded': result.image,
            }
            return render(request, 'recommend/result_text.html', context)
    else:
        form = ImageAnalysisForm()
    context = {
        'title': '이미지 분석',
        'form': form,
    }
    return render(request, 'recommend/upload_form.html', context)


# 경로 결정부터 결과 출력까지 처리
def recommend_flow(request):
    if request.method == 'POST':
        form = RecommendationForm(request.POST)
        if form.is_valid():
            result = form.save(commit=False)
            response = proxy_post('/decide-route', {'prompt': result.request_text})
            if response.status_code != 200:
                context = {'user_input': result.request_text, 'status_code': response.status_code}
                return render(request, 'recommend/error.html', context, status=503)
            result.route = response.json()['route']

            if result.route == '/images/generations':
                payload = {'prompt': result.request_text}
            else:
                payload = {
                    'messages': [
                        {'role': 'developer', 'content': RECOMMEND_SYSTEM_PROMPT},
                        {'role': 'user', 'content': result.request_text},
                    ],
                }
            response = proxy_post(result.route, payload)
            if response.status_code == 403:
                return render(request, 'recommend/rejected.html', {'user_input': result.request_text}, status=403)
            if response.status_code != 200:
                context = {'user_input': result.request_text, 'status_code': response.status_code}
                return render(request, 'recommend/error.html', context, status=503)
            data = response.json()
            image_base64 = ''
            if result.route == '/images/generations':
                image_base64 = data['image_base64']
            else:
                result.content = data['content']
            result.save()
            context = {'title': 'API 흐름 제어', 'result': result, 'image_base64': image_base64}
            return render(request, 'recommend/recommend_flow.html', context)
    else:
        form = RecommendationForm()
    return render(request, 'recommend/input_form.html', {'title': 'API 흐름 제어', 'form': form})
