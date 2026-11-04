from django.shortcuts import render, redirect
from .models import Author, Book
from .forms import AuthorForm, BookForm

# Create your views here.
def index(request):
    authors = Author.objects.all()
    context = {
        'authors': authors,
    }
    return render(request, 'libraries/index.html', context)

def detail(request, author_pk):
    author = Author.objects.get(pk=author_pk)
    book_form = BookForm()
    books = author.book_set.all()
    context = {
        'author': author,
        'book_form': book_form,
        'books': books,
    }
    return render(request, 'libraries/detail.html', context)