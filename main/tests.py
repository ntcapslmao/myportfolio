from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Education, CreativeProject, PortfolioItem

class MainPageTest(TestCase):
    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

        self.assertContains(response, f'href="{reverse("main:show_experience")}"')
        self.assertContains(response, f'href="{reverse("main:show_education")}"')
        self.assertContains(response, f'href="{reverse("main:show_portfolio")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-random-ngasal-yang-gaada-hehe/")
        self.assertEqual(response.status_code, 404)
class ExperienceTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Staff of Documentation and Animation",
            organisation="COMPFEST 18",
            description="Captured and edited high-resolution photography and videography for COMPFEST 18, a one-stop annual IT event organized by the students of the Faculty of Computer Science, Universitas Indonesia.",
            category="volunteer",
            started_at="2026-04-01"
        )

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Staff of Documentation and Animation")
        self.assertEqual(self.experience.category, "volunteer")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page_renders_data(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Volunteer")

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertNotContains(response, "Present")

class EducationTest(TestCase):
    def setUp(self):
        self.education = Education.objects.create(
            degree="Bachelor of Computer Science",
            institution="Universitas Indonesia",
            description="Relevant coursework: Foundations of Programming 1, Foundations of Programming 2, Linear Algebra, Digital Systems, and Computer Architecture.",
            started_at="2025-08-01",
            ended_at="2029-06-01"
        )

    def test_education_page_renders_data(self):
        response = self.client.get(reverse("main:show_education"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education.html")
        self.assertContains(response, self.education.degree)
        self.assertContains(response, self.education.institution)

    def test_empty_education_page(self):
        Education.objects.all().delete()
        response = self.client.get(reverse("main:show_education"))

        self.assertContains(response, "Belum ada riwayat pendidikan yang ditambahkan.")

class PortfolioTest(TestCase):
    def setUp(self):
        self.project = CreativeProject.objects.create(
            title="Personal Photography Hunts",
            description="Personal photography taken from my travels.",
            started_at="2024-01-01"
        )

        self.item = PortfolioItem.objects.create(
            project=self.project,
            title="Photo of Tugu Yogyakarta.",
            image_url="/static/img/tugu.jpg"
        )

    def test_portfolio_model_relation(self):
        self.assertEqual(self.item.project.title, "Personal Photography Hunts") # type: ignore

    def test_portfolio_page_renders_data(self):
        response = self.client.get(reverse("main:show_portfolio"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "portfolio.html")
        self.assertContains(response, self.project.title)
        self.assertContains(response, self.project.description)
        self.assertContains(response, self.item.image_url) # type: ignore
        self.assertContains(response, self.item.title)

    def test_empty_portfolio_page(self):
        CreativeProject.objects.all().delete()
        response = self.client.get(reverse("main:show_portfolio"))

        self.assertContains(response, "Belum ada creative work yang ditambahkan.")