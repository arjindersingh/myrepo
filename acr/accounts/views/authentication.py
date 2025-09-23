from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth import login, get_user_model, get_backends
from accounts.forms.registration import RegisterForm
from axes.handlers.proxy import AxesProxyHandler
from home.settings import AXES_RESET_ON_SUCCESS
from axes.utils import reset as axes_reset
from django.contrib.auth.views import PasswordResetConfirmView
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse_lazy

User = get_user_model()


def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        ip_address = request.META.get("REMOTE_ADDR")  # Get user's IP address

        # ✅ Check if the IP or username is locked
        if AxesProxyHandler.is_locked(request): 
            messages.error(request, "Account locked due to too many failed login attempts. Try again later.")
            return redirect("/")  # Redirect to home or login page

        # ✅ Check if the user exists
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")
            return redirect("/")  # Redirect to login page

        # ✅ Check if the user is active
        if not user.is_active:
            messages.error(request, "Your account is disabled. Contact support.")
            return redirect("/")

        # ✅ Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # ✅ Explicitly set authentication backend
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            
            # ✅ Reset failed login attempts for this user
            axes_reset(username=username)  # ✅ No ip_address argument required

            login(request, user)
            #messages.success(request, "Login successful!")
            return redirect("ShowDashboard")  # Redirect to dashboard
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "home.html")



def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("/")

def show_dashboard(request):
    return render(request, "dashboard.html")



def register_user(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # ✅ Explicitly set authentication backend
            backend = get_backends()[0]
            user.backend = f"{backend.__module__}.{backend.__class__.__name__}"

            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect("/")
    else:
        form = RegisterForm()
    
    return render(request, "registeruser.html", {"form": form})


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

    def form_valid(self, form):
        response = super().form_valid(form)

        # Send new password email
        user = self.user
        if user and user.email:
            send_mail(
                subject='Your Password Was Changed',
                message=f'Hi {user.get_full_name() or user.username},\n\nYour password has been successfully changed.\nIf you did not do this, please contact support immediately.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )

        return response
 