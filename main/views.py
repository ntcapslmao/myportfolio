from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from main.forms import ProjectForm
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

def show_experience(request):
    context = {
        "name": "Muhammad Ghazi Alfisyahri Latief",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

def show_education(request):
    education_list = Education.objects.all().order_by("-started_at")

    context = {
        "name": "Muhammad Ghazi Alfisyahri Latief",
        "education_list": education_list
    }

    return render(request, "education.html", context)

def show_portfolio(request):
    projects = CreativeProject.objects.prefetch_related("items").order_by("-started_at")

    context = {
        "name": "Muhammad Ghazi Alfisyahri Latief",
        "projects": projects
    }

    return render(request, "portfolio.html", context)

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
            messages.success(request, "Project berhasil dihapus!")
        else:
            messages.error(request, "Project gagal dihapus: Kata sandi salah!")

        return redirect("main:show_projects")

    return redirect("main:show_projects")

def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize("json", projects)
    return HttpResponse(projects_json, content_type="application/json")