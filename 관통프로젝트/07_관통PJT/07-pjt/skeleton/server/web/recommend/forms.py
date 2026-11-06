from django import forms
from .models import Recommendation, ImageAnalysis


class ImageAnalysisForm(forms.ModelForm):
    image = forms.ImageField(label='책 표지 사진 (png/jpg)')
    question = forms.CharField(
        label='질문',
        max_length=300,
        initial='이 책은 어떤 책이고, 비슷한 책을 추천해줘',
    )

    class Meta:
        model = ImageAnalysis
        fields = ['image', 'question']


class RecommendationForm(forms.ModelForm):
    request_text = forms.CharField(
        label='읽고 싶은 책의 취향을 알려주세요',
        max_length=300,
        widget=forms.Textarea(attrs={
            'rows': 5,
            'placeholder': '예) 출퇴근길에 가볍게 읽을 힐링 소설 추천해줘',
        }),
    )

    class Meta:
        model = Recommendation
        fields = ['request_text']
