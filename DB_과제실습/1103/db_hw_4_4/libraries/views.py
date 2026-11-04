from django.shortcuts import render, redirect
from .models import Book, Review
from .forms import BookForm, ReviewForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

# Create your views here.
def index(request):
    books = Book.objects.all()
    context = {
        'books': books
    }
    return render(request, 'libraries/index.html', context)

def detail(request, book_pk):
    book = Book.objects.get(pk=book_pk)
    review_form = ReviewForm()
    reviews = book.review_set.all()
    context = {
        'book': book,
        'review_form': review_form,
        'reviews': reviews,
    }
    return render(request, 'libraries/detail.html', context)

@login_required
@require_POST
def reviews_create(request, book_pk):
    book = Book.objects.get(pk=book_pk)
    review_form = ReviewForm(request.POST)
    if review_form.is_valid():
        review = review_form.save(commit=False)
        review.book = book
        review.user = request.user
        review.save()
        return redirect('libraries:detail', book.pk)
    reviews = book.review_set.all()
    context = {
        'book': book,
        'review_form': review_form,
        'reviews': reviews,
    }
    return render(request, 'libraries/detail.html', context)

def reviews_delete(request, book_pk, review_pk):
    review = Review.objects.get(pk=review_pk)
    if request.user == review.user:
        review.delete()
    return redirect('libraries:detail', book_pk)