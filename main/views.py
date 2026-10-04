from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.db.models import Q, F
from django.views.decorators.http import require_POST
from main.forms import ExperienceForm, ProjectForm, EducationForm, CreativeProjectForm
from main.models import Experience, Education, CreativeProject, Project

import datetime

def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request,user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        messages.success(request, "Akun berhasil dibuat! Silakan lakukan login.")
        return response

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
    title_query = request.GET.get("title", "").strip()
    is_editor = request.user.groups.filter(name='Editor').exists() if request.user.is_authenticated else False

    context = {
        "name": "Muhammad Ghazi Alfisyahri Latief",
        "title_query": title_query,
        "form": ExperienceForm(),
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

@require_POST
def create_experience_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan pengalaman."},
            status=403,
        )

    form = ExperienceForm(request.POST)
    if form.is_valid():
        experience = form.save()
        return JsonResponse(
            {"message": "Pengalaman berhasil ditambahkan.",
             "pk": str(experience.id)},
             status=201,
        )

    print("EXPERIENCE FORM ERRORS:", form.errors)

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)

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

    data = []
    for exp in experiences:
        is_starred = False
        if request.user.is_authenticated:
            is_starred = exp.starred_by.filter(id=request.user.id).exists()

        starred_users = exp.starred_by.all()
        starred_by_names = ", ".join([u.username for u in starred_users])

        data.append({
            "pk": str(exp.id),
            "fields": {
                "title": exp.title,
                "organisation": exp.organisation,
                "category": exp.category,
                "description": exp.description,
                "thumbnail": str(exp.thumbnail) if exp.thumbnail else "",
                "started_at_formatted": exp.started_at.strftime("%b %Y") if exp.started_at else "",
                "ended_at_formatted": exp.ended_at.strftime("%b %Y") if exp.ended_at else "",
                "is_ongoing": exp.is_ongoing,
                "star_count": starred_users.count(),
                "is_starred": is_starred,
                "starred_by_names": starred_by_names, 
            }
        })

    return JsonResponse(data, safe=False)

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
    title_query = request.GET.get("title", "").strip()
    is_editor = request.user.groups.filter(name='Editor').exists() if request.user.is_authenticated else False

    context = {
        "name": "Muhammad Ghazi Alfisyahri Latief",
        "title_query": title_query,
        "form": EducationForm(),
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

@require_POST
def create_education_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan riwayat pendidikan."}, 
            status=403
        )

    form = EducationForm(request.POST)
    if form.is_valid():
        education = form.save()
        return JsonResponse(
            {"message": "Pendidikan berhasil ditambahkan.", 
             "pk": str(education.id)}, 
             status=201
        )

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)

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

    data = []
    for edu in educations:
        is_starred = False
        if request.user.is_authenticated:
            is_starred = edu.starred_by.filter(id=request.user.id).exists()

        starred_users = edu.starred_by.all()
        starred_by_names = ", ".join([u.username for u in starred_users])

        data.append({
            "pk": str(edu.id),
            "fields": {
                "institution": edu.institution,
                "degree": edu.degree,
                "description": edu.description,
                "started_at_formatted": edu.started_at.strftime("%Y") if edu.started_at else "",
                "ended_at_formatted": edu.ended_at.strftime("%Y") if edu.ended_at else "Present",
                "star_count": starred_users.count(),
                "is_starred": is_starred,
                "starred_by_names": starred_by_names,
            }
        })
    
    return JsonResponse(data, safe=False)

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
    is_editor = request.user.groups.filter(name='Editor').exists() if request.user.is_authenticated else False

    context = {
        "name": "Muhammad Ghazi Alfisyahri Latief",
        "title_query": title_query,
        "form": CreativeProjectForm(),
        "is_editor": is_editor,
    }

    return render(request, "portfolio.html", context)

@require_POST
def create_portfolio_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan creative project."}, 
            status=403
        )

    form = CreativeProjectForm(request.POST)
    if form.is_valid():
        project = form.save()
        return JsonResponse(
            {"message": "Creative Project berhasil dibuat. Tambahkan foto/video melalui Django Admin.", 
             "pk": str(project.id)}, 
             status=201
        )

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)

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

    data = []
    for project in projects:
        is_starred = False
        if request.user.is_authenticated:
            is_starred = project.starred_by.filter(id=request.user.id).exists()

        starred_users = project.starred_by.all()
        starred_by_names = ", ".join([u.username for u in starred_users])

        portfolio_items = []
        for item in project.items.all(): # type: ignore
            portfolio_items.append({
                "title": item.title,
                "image_url": item.image_url if item.image_url else "",
                "video_embed_url": item.video_embed_url if item.video_embed_url else "",
            })

        data.append({
            "pk": str(project.id),
            "fields": {
                "title": project.title,
                "description": project.description,
                "started_at_formatted": project.started_at.strftime("%b %Y") if project.started_at else "",
                "ended_at_formatted": project.ended_at.strftime("%b %Y") if project.ended_at else "Present",
                "portfolio_items": portfolio_items,
                "star_count": starred_users.count(),
                "is_starred": is_starred,
                "starred_by_names": starred_by_names,
            }
        })
    return JsonResponse(data, safe=False)

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
    title_query = request.GET.get("title", "").strip()

    is_editor = request.user.groups.filter(name='Editor').exists() if request.user.is_authenticated else False

    context = {
        "name": "Muhammad Ghazi Alfisyahri Latief",
        "title_query": title_query,
        "form": ProjectForm(),
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

@require_POST
def create_project_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan proyek."},
            status=403,
        )

    form = ProjectForm(request.POST)
    if form.is_valid():
        project = form.save()
        return JsonResponse(
            {"message": "Proyek berhasil ditambahkan.", "pk": str(project.id)},
            status=201,
        )

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)

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

    data = []
    for project in projects:
        is_starred = False
        if request.user.is_authenticated:
            is_starred = project.starred_by.filter(id=request.user.id).exists()
            
        starred_users = project.starred_by.all()
        starred_by_names = ", ".join([u.username for u in starred_users])

        data.append({
            "pk": str(project.id),
            "fields": {
                "title": project.title,
                "description": project.description,
                "tech_stack": project.tech_stack,
                "project_url": str(project.project_url) if project.project_url else "",
                "project_image_url": str(project.project_image_url) if project.project_image_url else "",                "star_count": starred_users.count(),
                "is_starred": is_starred,
                "starred_by_names": starred_by_names,
            }
        })
    
    return JsonResponse(data, safe=False)

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