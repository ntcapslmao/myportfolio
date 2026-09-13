from django.urls import path

from main.views import show_main, show_experience, show_education, show_portfolio

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("education/", show_education, name="show_education"),
    path("portfolio/", show_portfolio, name="show_portfolio"),
]