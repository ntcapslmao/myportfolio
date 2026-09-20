from django.urls import path

from main.views import (
    show_main, 
    show_experience, create_experience, delete_experience, get_experience_json,
    show_education, create_education, delete_education, get_education_json,
    show_portfolio, create_portfolio, delete_portfolio,
    show_projects, create_project, delete_project, get_projects_json, 
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),

    path("experience/", show_experience, name="show_experience"),
    path("experience/add/", create_experience, name="create_experience"),
    path("api/experience/", get_experience_json, name="get_experience_json"),
    path("experience/<uuid:experience_id>/delete/", delete_experience, name="delete_experience"),

    path("education/", show_education, name="show_education"),
    path("education/add/", create_education, name="create_education"),
    path("api/education/", get_education_json, name="get_education_json"),
    path("education/<uuid:experience_id>/delete/", delete_education, name="delete_education"),

    path("portfolio/", show_portfolio, name="show_portfolio"),
    path("portfolio/add/", create_portfolio, name="create_portfolio"),
    path("portfolio/<uuid:project_id>/delete/", delete_portfolio ,name="delete_portfolio"),

    path("projects/", show_projects, name="show_projects"),
    path("projects/add/", create_project, name="create_project"),
    path("api/projects/", get_projects_json, name="get_projects_json"),
    path("projects/<uuid:project_id>/delete/", delete_project ,name="delete_project"),
]