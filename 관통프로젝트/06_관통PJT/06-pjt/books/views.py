from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST, require_safe
from django.core.exceptions import PermissionDenied
from .models import Book, Thread, Comment, Category
from .forms import BookForm, ThreadForm, CommentForm

# Create your views here.
@require_safe
def index(request):
    books = Book.objects.select_related('user', 'category').order_by('-pk')
    categories = Category.objects.all()
    category_pk = request.GET.get('category')
    if category_pk:
        books = books.filter(category_id=category_pk)

    context = {
        'books': books,
        'categories': categories,
        'selected_category': category_pk,
    }
    return render(request, 'books/index.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.user = request.user
            book.save()
            return redirect('books:detail', book.pk)
    
    else:
        form = BookForm()

    context = {
        'form': form,
    }
    return render(request, 'books/create.html', context)


@require_safe
def detail(request, book_pk):
    book = get_object_or_404(Book.objects.select_related('user'), pk=book_pk)
    threads = book.threads.select_related('user').order_by('-created_at')
    context = {
        'book': book,
        'threads': threads,
    }
    return render(request, 'books/detail.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def update(request, book_pk):
    book = get_object_or_404(Book, pk=book_pk)
    if request.user != book.user:
        raise PermissionDenied

    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('books:detail', book.pk)
    
    else:
        form = BookForm(instance=book)

    context = {
        'form': form,
        'book': book,
    }
    return render(request, 'books/update.html', context)


@login_required
@require_POST
def delete(request, book_pk):
    book = get_object_or_404(Book, pk=book_pk)
    if request.user != book.user:
        raise PermissionDenied

    book.delete()
    return redirect('books:index')


@login_required
@require_http_methods(['GET', 'POST'])
def thread_create(request, book_pk):
    book = get_object_or_404(Book, pk=book_pk)
    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.book = book
            thread.user = request.user
            thread.save()
            return redirect('books:thread_detail', thread.pk)
    
    else:
        form = ThreadForm()

    context = {
        'form': form,
        'book': book,
    }
    return render(request, 'books/thread_create.html', context)


@require_safe
def thread_detail(request, thread_pk):
    thread = get_object_or_404(Thread.objects.select_related('book', 'user'), pk=thread_pk)
    is_liked = False
    if request.user.is_authenticated:
        is_liked = thread.like_users.filter(pk=request.user.pk).exists()

    context = {
        'thread': thread,
        'is_liked': is_liked,
        'comments': thread.comments.select_related('user').order_by('-created_at'),
        'comment_form': CommentForm(),
    }
    return render(request, 'books/thread_detail.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def thread_update(request, thread_pk):
    thread = get_object_or_404(Thread, pk=thread_pk)
    if request.user != thread.user:
        raise PermissionDenied

    if request.method == 'POST':
        form = ThreadForm(request.POST, instance=thread)
        if form.is_valid():
            form.save()
            return redirect('books:thread_detail', thread.pk)
   
    else:
        form = ThreadForm(instance=thread)

    context = {
        'form': form,
        'thread': thread,
    }
    return render(request, 'books/thread_update.html', context)


@login_required
@require_POST
def thread_delete(request, thread_pk):
    thread = get_object_or_404(Thread, pk=thread_pk)
    if request.user != thread.user:
        raise PermissionDenied

    book_pk = thread.book.pk
    thread.delete()
    return redirect('books:detail', book_pk)


@login_required
@require_POST
def like(request, thread_pk):
    thread = get_object_or_404(Thread, pk=thread_pk)
    if thread.like_users.filter(pk=request.user.pk).exists():
        thread.like_users.remove(request.user)
    
    else:
        thread.like_users.add(request.user)

    return redirect('books:thread_detail', thread.pk)


@login_required
@require_POST
def comment_create(request, thread_pk):
    thread = get_object_or_404(Thread, pk=thread_pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.thread = thread
        comment.user = request.user
        comment.save()
    return redirect('books:thread_detail', thread.pk)


@login_required
@require_POST
def comment_delete(request, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    if comment.user != request.user:
        raise PermissionDenied

    thread_pk = comment.thread.pk
    comment.delete()
    return redirect('books:thread_detail', thread_pk)