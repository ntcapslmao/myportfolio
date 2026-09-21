from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.conf import settings

from main.models import Experience, Education, CreativeProject, PortfolioItem, Project

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

    def test_create_experience(self):
        settings.SECRET_PASSWORD = "akucintaburhan42069"
        response = self.client.post(reverse("main:create_experience"), {
            "title": "Staf Dokumentasi",
            "organisation": "OH Fasilkom UI 25",
            "category": "volunteer",
            "started_at": "2025-08-01",
            "description": "Tukang cekrek keliling pas OH 25.",
            "passcode": "akucintaburhan42069"
        })

        self.assertRedirects(response, reverse("main:show_experience"))
        self.assertEqual(Experience.objects.count(), 2)

    def test_delete_experience(self):
        settings.SECRET_PASSWORD = "akucintaburhan42069"
        failed_response = self.client.post(
            reverse("main:delete_experience", args=[self.experience.id]),
            {"passcode": "ngawur cik yifutvgdsr ubthgvybfdx"}
        )
        self.assertEqual(Experience.objects.count(), 1)

        successful_response = self.client.post(
            reverse("main:delete_experience", args=[self.experience.id]),
            {"passcode": "akucintaburhan42069"}
        )
        self.assertEqual(Experience.objects.count(), 0)

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

    def test_education_search(self):
        response = self.client.get(reverse("main:show_education"), {"title": "Bachelor of Computer Science"})
        self.assertContains(response, "Universitas Indonesia")

    def test_delete_education(self):
        settings.SECRET_PASSWORD = "akucintaburhan42069"
        response = self.client.post(
            reverse("main:delete_education", args=[self.education.id]),
            {"passcode": "akucintaburhan42069"}
        )
        self.assertEqual(Education.objects.count(), 0)

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

    def test_delete_portfolio(self):
        settings.SECRET_PASSWORD = "akucintaburhan42069"
        response = self.client.post(
            reverse("main:delete_portfolio", args=[self.project.id]),
            {"passcode": "akucintaburhan42069"}
        )
        self.assertEqual(CreativeProject.objects.count(), 0)
        self.assertEqual(PortfolioItem.objects.count(), 0)

class ProjectTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title="BurhanQuest",
            description="Membangun game RPG dengan Java CLI saat DDP2.",
            tech_stack="Git, Java",
            project_url="https://github.com/ntcapslmao/"
        )

        settings.SECRET_PASSWORD = "akucintaburhan42069"

    def test_project_model(self):
        self.assertEqual(str(self.project), "BurhanQuest")
        self.assertEqual(self.project.tech_stack, "Git, Java")

    def test_project_page_renders_data(self):
        response = self.client.get(reverse("main:show_projects"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project.html")
        self.assertContains(response, self.project.title)
        self.assertContains(response, self.project.description)

    def test_empty_project_page(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("main:show_projects"))
        self.assertContains(response, "Belum ada proyek yang ditambahkan.")

    def test_project_search_functionality(self):
        response = self.client.get(reverse("main:show_projects"), {"title": "BurhanQuest"})
        self.assertContains(response, "BurhanQuest")

        empty_response = self.client.get(reverse("main:show_projects"), {"title": "asihjnbudihudashuidas"})
        self.assertContains(empty_response, "Tidak ada proyek dengan nama tersebut.")

    def test_delete_project_wrong_password(self):
        response = self.client.post(
            reverse("main:delete_project", args=[self.project.id]),
            {"passcode": "sdfihuohujiofdsogyhuidf"}
        )

        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertEqual(Project.objects.count(), 1)

    def test_delete_project_correct_password(self):
        response = self.client.post(
            reverse("main:delete_project", args=[self.project.id]),
            {"passcode": "akucintaburhan42069"}
        )

        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertEqual(Project.objects.count(), 0)