from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.db.models import Q, F
from main.forms import ExperienceForm, ProjectForm, EducationForm, CreativeProjectForm
from main.models import Experience, Education, CreativeProject, Project

import datetime

def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat! Silakan lakukan login.")

    context = {
        "name": "Muhammad Ghazi Alfisyahri Latief",
        "form": form,
    }

    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "name": "Muhammad Ghazi Alfisyahri Latief",
        "form": form,
    }

    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response

def show_main(request):
    last_login = request.COOKIES.get('last_login', 'Belum ada sesi login atau Cookie tidak ditemukan.')
    context = {
        "name": "Muhammad Ghazi Alfisyahri Latief",
        "npm": "2506537751",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "Second-Year Undergraduate Student @ Faculty of Computer Science, Universitas Indonesia with a keen interest in game development, data science, and software engineering."
        ),
        "last_login": last_login,
    }
    return render(request, "index.html", context)

# atas main, bawah exp

def show_experience(request):
    json_response = get_experience_json(request)

    experiences = serializers.deserialize(
        "json", json_response.content.decode("utf-8")
    )
    experiences = [exp.object for exp in experiences]
    title_query = request.GET.get("title", "").strip()

    is_editor = request.user.groups.filter(name='Editor').exists() if request.user.is_authenticated else False

    context = {
        "name": "Muhammad Ghazi Alfisyahri Latief",
        "experience_list": experiences,
        "title_query": title_query,
        "is_editor": is_editor,
    }
    return render(request, "experience.html", context)

@login_required(login_url="/login/")
def create_experience(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    form = ExperienceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pengalaman baru berhasil ditambahkan!")
        return redirect("main:show_experience")

    context = {
        "name": "Muhammad Ghazi Alfisyahri Latief",
        "form": form
    }

    return render(request, "experience_form.html", context)

@login_required(login_url="/login/")
def delete_experience(request, experience_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        input_passcode = request.POST.get("passcode")

        if input_passcode == settings.SECRET_PASSWORD:
            experience.delete()
            messages.success(request, "Pengalaman berhasil dihapus.")
        else:
            messages.error(request, "Gagal menghapus: Kata sandi salah!")
        
        return redirect("main:show_experience")

    return redirect("main:show_experience")

def get_experience_json(request):
    title_query = request.GET.get("title", "").strip()
    experiences = Experience.objects.all().order_by(F('ended_at').desc(nulls_first=True), 'started_at')

    if title_query:
        experiences = experiences.filter(title__icontains=title_query)

    experience_json = serializers.serialize("json", experiences, use_natural_foreign_keys=True)
    return HttpResponse(experience_json, content_type="application/json")

@login_required(login_url="/login/")
def edit_experience(request, experience_id):
    is_editor = request.user.groups.filter(name='Editor').exists()

    if not (request.user.is_superuser or is_editor):
        raise PermissionDenied
    
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        form = ExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            messages.success(request, f"Data '{experience.title}' berhasil diperbarui!")
            return redirect("main:show_experience")
    else:
        form = ExperienceForm(instance=experience)

    context = {
        "name": "Muhammad Ghazi Alfisyahri Latief",
        "form": form,
        "is_edit": True 
    }
    return render(request, "experience_form.html", context)

@login_required(login_url="/login/")
def toggle_star_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        if request.user in experience.starred_by.all():
            experience.starred_by.remove(request.user)
        else:
            experience.starred_by.add(request.user)

    return redirect("main:show_experience")

# atas exp, bawah edu

def show_education(request):
    json_response = get_education_json(request)

    educations = serializers.deserialize(
        "json", json_response.content.decode("utf-8")
    )
    educations = [edu.object for edu in educations]
    title_query = request.GET.get("title", "").strip()

    is_editor = request.user.groups.filter(name='Editor').exists() if request.user.is_authenticated else False

    context = {
        "name": "Muhammad Ghazi Alfisyahri Latief",
        "education_list": educations,
        "title_query": title_query,
        "is_editor": is_editor,
    }

    return render(request, "education.html", context)

@login_required(login_url="/login/")
def create_education(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    form = EducationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Riwayat pendidikan berhasil ditambahkan.")
        return redirect("main:show_education")

    context = {
        "name": "Muhammad Ghazi Alfisyahri Latief",
        "form": form
    }
    return render(request, "education_form.html", context)

@login_required(login_url="/login/")
def delete_education(request, education_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    education = get_object_or_404(Education, pk=education_id)

    if request.method == "POST":
        input_passcode = request.POST.get("passcode")

        if input_passcode == settings.SECRET_PASSWORD:
            education.delete()
            messages.success(request, "Riwayat pendidikan berhasil dihapus.")
        else:
            messages.error(request, "Gagal menghapus: Kata sandi salah.")
        return redirect("main:show_education")
    return redirect("main:show_education")

def get_education_json(request):
    title_query = request.GET.get("title", "").strip()
    educations = Education.objects.all().order_by("-started_at")

    if title_query:
        educations = educations.filter(
            Q(institution__icontains=title_query) | Q(degree__icontains=title_query)
        )

    education_json = serializers.serialize("json", educations, use_natural_foreign_keys=True)
    return HttpResponse(education_json, content_type="application/json")

@login_required(login_url="/login/")
def edit_education(request, education_id):
    is_editor = request.user.groups.filter(name='Editor').exists()

    if not (request.user.is_superuser or is_editor):
        raise PermissionDenied
    
    education = get_object_or_404(Education, pk=education_id)
    if request.method == "POST":
        form = EducationForm(request.POST, instance=education)
        if form.is_valid():
            form.save()
            messages.success(request, f"Riwayat pendidikan {education.degree} di {education.institution} telah diperbarui.")
            return redirect("main:show_education")
    else:
        form = EducationForm(instance=education)

    context = {
            "name": "Muhammad Ghazi Alfisyahri Latief",
            "form": form,
            "is_edit": True
        }
    return render(request, "education_form.html", context)

@login_required(login_url="/login/")
def toggle_star_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)

    if request.method == "POST":
        if request.user in education.starred_by.all():
            education.starred_by.remove(request.user)
        else:
            education.starred_by.add(request.user)

    return redirect("main:show_education")

# atas edu, bawah porto

def show_portfolio(request):
    title_query = request.GET.get("title", "").strip()
    projects = CreativeProject.objects.prefetch_related("items").order_by("-started_at")

    is_editor = request.user.groups.filter(name='Editor').exists() if request.user.is_authenticated else False

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    context = {
        "name": "Muhammad Ghazi Alfisyahri Latief",
        "projects": projects,
        "title_query": title_query,
        "is_editor": is_editor
    }

    return render(request, "portfolio.html", context)

@login_required(login_url="/login/")
def create_portfolio(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    form = CreativeProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Wadah CreativeProject berhasil dibuat! Akibat keterbatasan sistem, buka Django Admin untuk menambahkan foto/video.")
        return redirect("main:show_portfolio")

    context = {
        "name": "Muhammad Ghazi Alfisyahri Latief",
        "form": form
    }
    return render(request, "portfolio_form.html", context)

@login_required(login_url="/login/")
def delete_portfolio(request, project_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    project = get_object_or_404(CreativeProject, pk=project_id)

    if request.method == "POST":
        input_passcode = request.POST.get("passcode")

        if input_passcode == settings.SECRET_PASSWORD:
            project.delete()
            messages.success(request, "CreativeWork serta segala item didalamnya berhasil dihapus.")
        else:
            messages.error(request, "Gagal menghapus: Kata sandi salah.")
        
        return redirect("main:show_portfolio")
    return redirect("main:show_portfolio")

def get_portfolio_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = CreativeProject.objects.all()
    if title_query:
        projects = projects.filter(title__icontains=title_query)
    return HttpResponse(serializers.serialize("json", projects, use_natural_foreign_keys=True), content_type="application/json")

@login_required(login_url="/login/")
def edit_portfolio(request, project_id):
    is_editor = request.user.groups.filter(name='Editor').exists()

    if not (request.user.is_superuser or is_editor):
        raise PermissionDenied
    
    project = get_object_or_404(CreativeProject, pk=project_id)
    if request.method == "POST":
        form = CreativeProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f"Creative project {project.title} telah diperbarui.")
            return redirect("main:show_portfolio")
    else:
        form = CreativeProjectForm(instance=project)

    context = {
            "name": "Muhammad Ghazi Alfisyahri Latief",
            "form": form,
            "is_edit": True
        }
    return render(request, "portfolio_form.html", context)

@login_required(login_url="/login/")
def toggle_star_portfolio(request, project_id):
    project = get_object_or_404(CreativeProject, pk=project_id)

    if request.method == "POST":
        if request.user in project.starred_by.all():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)

    return redirect("main:show_portfolio")

# atas porto, bawah project

def show_projects(request):
    json_response = get_projects_json(request)

    projects = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    projects = [project.object for project in projects]
    title_query = request.GET.get("title", "").strip()

    is_editor = request.user.groups.filter(name='Editor').exists() if request.user.is_authenticated else False

    context = {
        "name": "Muhammad Ghazi Alfisyahri Latief",
        "project_list": projects,
        "title_query": title_query,
        "is_editor": is_editor,
    }
    return render(request, "project.html", context)

@login_required(login_url="/login/")
def create_project(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_projects")

    context = {
            "name": "Muhammad Ghazi Alfisyahri Latief",
            "form": form
        }

    return render(request, "projects_form.html", context)

@login_required(login_url="/login/")
def delete_project(request, project_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        passcode_input = request.POST.get("passcode")
        if passcode_input == settings.SECRET_PASSWORD: 
            project.delete()
            messages.success(request, "Project berhasil dihapus.")
        else:
            messages.error(request, "Gagal dihapus: Kata sandi salah!")

        return redirect("main:show_projects")

    return redirect("main:show_projects")

def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize("json", projects, use_natural_foreign_keys=True)
    return HttpResponse(projects_json, content_type="application/json")

@login_required(login_url="/login/")
def edit_project(request, project_id):
    is_editor = request.user.groups.filter(name='Editor').exists()

    if not (request.user.is_superuser or is_editor):
        raise PermissionDenied

    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f"Proyek {project.title} berhasil diperbarui.")
            return redirect("main:show_projects")
    else:
        form = ProjectForm(instance=project)

    context = {
        "name": "Muhammad Ghazi Alfisyahri Latief",
        "form": form,
        "is_edit": True 
    }
    return render(request, "projects_form.html", context)

@login_required(login_url="/login/")
def toggle_star_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        if request.user in project.starred_by.all():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)

    return redirect("main:show_projects")