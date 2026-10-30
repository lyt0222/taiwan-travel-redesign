from django import forms
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render


class RegisterForm(UserCreationForm):
    email = forms.EmailField(label="電子郵件", required=False)

    class Meta:
        model = User
        fields = ("username", "email")
        labels = {"username": "帳號"}


class MemberLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f"歡迎回來，{form.get_user().username}！登入後可以收藏景點、安排我的行程。")
        return super().form_valid(form)


def register(request):
    if request.user.is_authenticated:
        return redirect("spots:home")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "註冊成功！現在可以把景點加入我的行程。")
            return redirect("spots:home")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})
