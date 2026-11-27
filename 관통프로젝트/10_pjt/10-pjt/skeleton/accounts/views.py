from django.http.response import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.views.decorators.http import (
    require_http_methods,
    require_POST,
)

from .forms import CustomUserCreationForm, CustomUserChangeForm


@require_http_methods(["GET", "POST"])
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


@require_POST
def logout(request):
    auth_logout(request)
    return redirect('books:index')


def signup(request):
    if request.user.is_authenticated:
        return redirect('books:index')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            selected_categories = form.cleaned_data.get('interested_genres')
            if selected_categories:
                user.interested_genres.set(selected_categories)
            auth_login(request, user)
            return redirect('books:index')
    else:
        form = CustomUserCreationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/signup.html', context)


def profile(request, username):
    User = get_user_model()
    person = User.objects.get(username=username)
    context = {
        'person': person,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
@require_POST
def follow(request, user_pk):
    person = get_object_or_404(get_user_model(), pk=user_pk)

    if request.user == person:
        return JsonResponse({"error": "자기 자신은 팔로우할 수 없습니다."}, status=400)

    followings = request.user.followings

    if followings.filter(pk=person.pk).exists():
        followings.remove(person)
        is_following = False
    else:
        followings.add(person)
        is_following = True

    return JsonResponse({
        "is_following": is_following,
        "followers_count": person.followers.count(),
        "followings_count": person.followings.count(),
    })