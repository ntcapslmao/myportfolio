from django.urls import path

from main.views import (
    show_main, show_experience, show_education, show_portfolio, create_project, show_projects,
    get_projects_json, delete_project
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("education/", show_education, name="show_education"),
    path("portfolio/", show_portfolio, name="show_portfolio"),
    path("projects/", show_projects, name="show_projects"),
    path("projects/add/", create_project, name="create_project"),
    path("api/projects/", get_projects_json, name="get_projects_json"),
    path("projects/<uuid:project_id>/delete/", delete_project ,name="delete_project"),
]