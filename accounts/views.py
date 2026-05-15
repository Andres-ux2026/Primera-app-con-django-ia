from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView as AuthLoginView
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User
from .forms import RegistroForm, LoginForm
from .decorators import admin_required


class LoginView(AuthLoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


class RegisterView(View):
    def get(self, request):
        form = RegistroForm()
        return render(request, 'accounts/register.html', {'form': form})

    def post(self, request):
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.Role.STUDENT
            user.is_approved = False
            user.save()
            messages.success(request, 'Registro exitoso. Un administrador debe aprobar tu cuenta antes de que puedas ingresar.')
            return redirect('accounts:login')
        return render(request, 'accounts/register.html', {'form': form})


class DashboardRedirectView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        if user.role == User.Role.STUDENT:
            if not user.is_approved:
                return render(request, 'accounts/pending_approval.html')
            return redirect('core:student_dashboard')
        elif user.role == User.Role.TEACHER:
            return redirect('core:teacher_subject_list')
        elif user.role == User.Role.ADMIN:
            return redirect('admin:index')
        return redirect('accounts:login')


class ApprovalListView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != User.Role.ADMIN:
            messages.error(request, 'No tienes permiso para acceder.')
            return redirect('home')
        pending_users = User.objects.filter(role=User.Role.STUDENT, is_approved=False)
        return render(request, 'accounts/approval_list.html', {'pending_users': pending_users})

    def post(self, request):
        if request.user.role != User.Role.ADMIN:
            messages.error(request, 'No tienes permiso para acceder.')
            return redirect('home')
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        user = get_object_or_404(User, id=user_id, role=User.Role.STUDENT)

        if action == 'approve':
            user.is_approved = True
            user.save()
            messages.success(request, f'Usuario {user.username} aprobado correctamente.')
        elif action == 'reject':
            user.delete()
            messages.success(request, f'Usuario {user.username} rechazado y eliminado.')

        return redirect('accounts:approval_list')
