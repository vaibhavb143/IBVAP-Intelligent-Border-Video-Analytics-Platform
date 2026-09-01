from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views import View

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:index')
        return render(request, 'accounts/login.html')

    def post(self, request):
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0) # expires on browser close
            else:
                request.session.set_expiry(1209600) # 2 weeks
            messages.success(request, f"Welcome to Command Center, Officer {user.get_full_name() or user.username}.")
            return redirect('dashboard:index')
        else:
            messages.error(request, "Invalid Officer ID or Security Credentials.")
            return render(request, 'accounts/login.html', {'username': username})

class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, "Officer signed out from Security Terminal.")
        return redirect('accounts:login')
    
    def post(self, request):
        logout(request)
        messages.info(request, "Officer signed out from Security Terminal.")
        return redirect('accounts:login')
