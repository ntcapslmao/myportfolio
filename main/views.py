from django.shortcuts import render
from main.models import Experience

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