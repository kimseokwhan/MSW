from django import forms
from .models import Book, Thread, Comment

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ('title', 'description', 'review_score', 'author', 'category')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'review_score': forms.NumberInput(attrs={
                'min': 0, 
                'max': 5, 
                'step': 0.1,
            }),
        }
    def clean_review_score(self):
        score = self.cleaned_data['review_score']
        if not 0 <= score <= 5:
            raise forms.ValidationError('평점은 0점부터 5점까지 입력해주세요.')
        return score


class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ('title', 'content', 'reading_date')
        widgets = {
            'content': forms.Textarea(attrs={'rows': 6}),
            'reading_date': forms.DateInput(attrs={'type': 'date'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': '댓글을 입력하세요.',
                })
        }