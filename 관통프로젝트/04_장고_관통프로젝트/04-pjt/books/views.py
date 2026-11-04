from django.shortcuts import render, redirect

from .forms import BookForm
from .models import Book

# Create your views here.
def index(request):
    books = Book.objects.all()
    context = {
        'books': books,
    }
    return render(request, 'books/index.html', context)

def create(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            return redirect('books:detail', book.pk)
    else:
        form = BookForm()
    context = {
        'form': form
    }
    return render(request, 'books/create.html', context)

def detail(request, book_pk):
    book = Book.objects.get(pk=book_pk)
    context = {
        'book': book,
    }
    return render(request, 'books/detail.html', context)

def delete(request, book_pk):
    if request.method == 'POST':
        book = Book.objects.get(pk=book_pk)
        book.delete()
    return redirect('books:index')

def update(request, book_pk):
    book = Book.objects.get(pk=book_pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('books:detail', book.pk)
        else:
            print(form.errors)
    else:
        form = BookForm(instance=book)
    context = {
        'book': book,
        'form': form,
    }
    return render(request, 'books/update.html', context)