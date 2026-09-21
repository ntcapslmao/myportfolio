from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.db.models import Q, F
from main.forms import ExperienceForm, ProjectForm, EducationForm, CreativeProjectForm
from main.models import Experience, Education, CreativeProject, Project

def show_main(request):
    context = {
        "name": "Muhammad Ghazi Alfisyahri Latief",
        "npm": "2506537751",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "Second-Year Undergraduate Student @ Faculty of Computer Science, Universitas Indonesia with a keen interest in game development, data science, and software engineering."
        ),
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

    context = {
        "name": "Muhammad Ghazi Alfisyahri Latief",
        "experience_list": experiences,
        "title_query": title_query,
    }
    return render(request, "experience.html", context)

def create_experience(request):
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

def delete_experience(request, experience_id):
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
    experiences = Experience.objects.all().order_by(F('ended_at').desc(nulls_first=True))

    if title_query:
        experiences = experiences.filter(title__icontains=title_query)

    experience_json = serializers.serialize("json", experiences)
    return HttpResponse(experience_json, content_type="application/json")

def edit_experience(request, experience_id):
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

# atas exp, bawah edu

def show_education(request):
    json_response = get_education_json(request)

    educations = serializers.deserialize(
        "json", json_response.content.decode("utf-8")
    )
    educations = [edu.object for edu in educations]
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Muhammad Ghazi Alfisyahri Latief",
        "education_list": educations,
        "title_query": title_query,
    }

    return render(request, "education.html", context)

def create_education(request):
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

def delete_education(request, education_id):
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

    education_json = serializers.serialize("json", educations)
    return HttpResponse(education_json, content_type="application/json")

def edit_education(request, education_id):
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

# atas edu, bawah porto

def show_portfolio(request):
    title_query = request.GET.get("title", "").strip()
    projects = CreativeProject.objects.prefetch_related("items").order_by("-started_at")

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    context = {
        "name": "Muhammad Ghazi Alfisyahri Latief",
        "projects": projects,
        "title_query": title_query,
    }

    return render(request, "portfolio.html", context)

def create_portfolio(request):
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

def delete_portfolio(request, project_id):
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
    return HttpResponse(serializers.serialize("json", projects), content_type="application/json")

def edit_portfolio(request, project_id):
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

# atas porto, bawah project

def show_projects(request):
    json_response = get_projects_json(request)

    projects = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    projects = [project.object for project in projects]
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Muhammad Ghazi Alfisyahri Latief",
        "project_list": projects,
        "title_query": title_query,
    }
    return render(request, "project.html", context)

def create_project(request):
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

def delete_project(request, project_id):
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

    projects_json = serializers.serialize("json", projects)
    return HttpResponse(projects_json, content_type="application/json")

def edit_project(request, project_id):
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