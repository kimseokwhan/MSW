from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST, require_safe
from .forms import CustomUserCreationForm, CustomUserChangeForm

# Create your views here.
User = get_user_model()

@require_http_methods(['GET', 'POST'])
def login(request):
    if request.user.is_authenticated:
        return redirect('books:index')

    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('books:index')

    else:
        form = AuthenticationForm()

    context = {
        'form': form,
    }
    return render(request, 'accounts/login.html', context)


@login_required
@require_POST
def logout(request):
    auth_logout(request)
    return redirect('books:index')


@require_http_methods(['GET', 'POST'])
def signup(request):
    if request.user.is_authenticated:
        return redirect('books:index')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('books:index')

    else:
        form = CustomUserCreationForm()

    context = {
        'form': form,
    }
    return render(request, 'accounts/signup.html', context)


@require_safe
def profile(request, username):
    person = get_object_or_404(User, username=username)
    threads = person.threads.select_related('book').order_by('-created_at')
    is_following = False
    if request.user.is_authenticated:
        is_following = request.user.followings.filter(pk=person.pk).exists()

    context = {
        'person': person,
        'threads': threads,
        'is_following': is_following,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
@require_POST
def follow(request, user_pk):
    person = get_object_or_404(User, pk=user_pk)
    if request.user != person:
        if request.user.followings.filter(pk=person.pk).exists():
            request.user.followings.remove(person)

        else:
            request.user.followings.add(person)

    return redirect('accounts:profile', person.username)


@login_required
@require_http_methods(['GET', 'POST'])
def update(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('books:index')

    else:
        form = CustomUserChangeForm(instance=request.user)

    context = {
        'form': form,
    }
    return render(request, 'accounts/update.html', context)


@login_required
@require_POST
def delete(request):
    request.user.delete()
    auth_logout(request)
    return redirect('books:index')


@login_required
@require_http_methods(['GET', 'POST'])
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('books:index')

    else:
        form = PasswordChangeForm(request.user)

    context = {
        'form': form,
    }
    return render(request, 'accounts/change_password.html', context)