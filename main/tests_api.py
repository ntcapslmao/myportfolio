import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Project, Experience, Education, CreativeProject


class ProjectAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.visitor = User.objects.create_user(username="visitor", password="test-password")
        self.project = Project.objects.create(
            title="Portfolio", description="My website", tech_stack="Django",
        )
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse("api:project-detail", args=[self.project.id])
        self.star_url = reverse("api:project-star", args=[self.project.id])
        self.payload = {
            "title": "New project", "description": "A useful app", "tech_stack": "Python",
            "project_url": "https://example.com/", "project_image_url": "",
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.project.id)) # type: ignore
        self.assertFalse(response.data[0]["is_starred"]) # type: ignore
        self.assertNotIn("fields", response.data[0]) # type: ignore
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": "PORT"})
        self.assertEqual(len(response.data), 1) # type: ignore
        response = self.client.get(self.list_url, {"title": "not-found"})
        self.assertEqual(response.data, []) # type: ignore

    def test_missing_project(self):
        url = reverse("api:project-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user) # type: ignore
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio")

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner) # type: ignore
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists()) # type: ignore

    def test_validation(self):
        self.client.force_authenticate(user=self.owner) # type: ignore
        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"project_url": "javascript:alert(1)"}, "project_url"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data) # type: ignore
        self.assertEqual(Project.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner) # type: ignore
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.description, "My website")
        response = self.client.put(self.detail_url, {"title": "Incomplete"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.visitor) # type: ignore
        response = self.client.post(self.star_url)
        self.assertTrue(response.data["is_starred"]) # type: ignore
        self.assertEqual(response.data["star_count"], 1) # type: ignore
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"]) # type: ignore
        self.assertEqual(response.data["star_count"], 0) # type: ignore

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner) # type: ignore
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True,
            "starred_by_names": "forged", "starred_by": [self.visitor.id], # type: ignore
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0) # type: ignore
        self.assertFalse(response.data["is_starred"]) # type: ignore

    def test_staff_and_editor_cannot_manage_tutorial_projects(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.visitor.groups.add(Group.objects.create(name="Editor"))
        self.client.force_authenticate(user=self.visitor) # type: ignore
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner) # type: ignore
        self.assertEqual(self.client.delete(self.list_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) # type: ignore
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        # The Browsable API form renders a real CSRF token into the response.
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK) # type: ignore
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED) # type: ignore


class EducationAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner_edu", password="test-password", email="owner_edu@example.com",
        )
        self.editor_group = Group.objects.create(name="Editor")
        self.editor = User.objects.create_user(username="editor_edu", password="test-password")
        self.editor.groups.add(self.editor_group)

        self.visitor = User.objects.create_user(username="visitor_edu", password="test-password")

        self.education = Education.objects.create(
            institution="Universitas Indonesia",
            degree="S1 Ilmu Komputer",
            description="Relevant coursework: DDP1, DDP2, SDA",
            started_at="2025-08-01",
            ended_at="2029-06-01",
        )
        self.list_url = reverse("api:education-list")
        self.detail_url = reverse("api:education-detail", args=[self.education.id])
        self.star_url = reverse("api:education-star", args=[self.education.id])
        self.payload = {
            "institution": "Institut Teknologi Bandung",
            "degree": "S2 Teknik Informatika",
            "description": "Studi pascasarjana bidang kecerdasan buatan",
            "started_at": "2029-08-01",
            "ended_at": "2031-06-01",
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.education.id)) # type: ignore
        self.assertFalse(response.data[0]["is_starred"]) # type: ignore
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": "Indonesia"})
        self.assertEqual(len(response.data), 1) # type: ignore
        response = self.client.get(self.list_url, {"title": "NonExistentInstitution"})
        self.assertEqual(response.data, []) # type: ignore

    def test_missing_education_returns_404(self):
        url = reverse("api:education-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user) # type: ignore
            # POST is rejected
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            # PATCH is rejected
            self.assertEqual(self.client.patch(self.detail_url, {"degree": "Hacked"}, format="json").status_code, 403)
            # DELETE is rejected
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)

        # Database state verification
        self.assertEqual(Education.objects.count(), 1)
        self.education.refresh_from_db()
        self.assertEqual(self.education.degree, "S1 Ilmu Komputer")

    def test_editor_can_patch_and_put_but_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor) # type: ignore

        # Editor cannot create (POST)
        post_resp = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(post_resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Education.objects.count(), 1)

        # Editor cannot delete
        del_resp = self.client.delete(self.detail_url)
        self.assertEqual(del_resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Education.objects.count(), 1)

        # Editor can PATCH
        patch_resp = self.client.patch(self.detail_url, {"degree": "S1 Ilmu Komputer (Cumlaude)"}, format="json")
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        self.education.refresh_from_db()
        self.assertEqual(self.education.degree, "S1 Ilmu Komputer (Cumlaude)")

        # Editor can PUT
        put_resp = self.client.put(self.detail_url, {
            "institution": "Universitas Indonesia",
            "degree": "S1 Ilmu Komputer (Honors)",
            "description": "Updated",
            "started_at": "2025-08-01",
            "ended_at": "2029-06-01",
        }, format="json")
        self.assertEqual(put_resp.status_code, status.HTTP_200_OK)
        self.education.refresh_from_db()
        self.assertEqual(self.education.degree, "S1 Ilmu Komputer (Honors)")

    def test_owner_can_create_and_delete(self):
        self.client.force_authenticate(user=self.owner) # type: ignore

        # Owner can create
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Education.objects.count(), 2)

        created_id = response.data["id"] # type: ignore
        detail_created_url = reverse("api:education-detail", args=[created_id])

        # Owner can delete
        del_resp = self.client.delete(detail_created_url)
        self.assertEqual(del_resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Education.objects.count(), 1)

    def test_validation_rejects_empty_or_xss_tags(self):
        self.client.force_authenticate(user=self.owner) # type: ignore
        for changes, field in [
            ({"institution": "   "}, "institution"),
            ({"institution": '<img src="x" onerror="alert(1)">'}, "institution"),
            ({"degree": "<b></b>"}, "degree"),
            ({"ended_at": "2020-01-01", "started_at": "2025-01-01"}, "ended_at"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data) # type: ignore
        self.assertEqual(Education.objects.count(), 1)

    def test_star_requires_login_and_toggles(self):
        # Guest denied
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)

        # Authenticated user can toggle star
        self.client.force_authenticate(user=self.visitor) # type: ignore
        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_starred"]) # type: ignore
        self.assertEqual(response.data["star_count"], 1) # type: ignore

        # Star again to unstar
        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_starred"]) # type: ignore
        self.assertEqual(response.data["star_count"], 0) # type: ignore

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner) # type: ignore
        response = self.client.post(self.list_url, {
            **self.payload,
            "star_count": 999,
            "is_starred": True,
            "starred_by_names": "fake_user",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0) # type: ignore
        self.assertFalse(response.data["is_starred"]) # type: ignore

    def test_csrf_protection_enforced(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner_edu", password="test-password"))

        # Request without CSRF token is rejected
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) # type: ignore
        self.assertEqual(Education.objects.count(), 1)

        # Request with CSRF token succeeds
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        token = client.cookies["csrftoken"].value
        response = client.post(self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED) # type: ignore
        self.assertEqual(Education.objects.count(), 2)


class ExperienceAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner_exp", password="test-password", email="owner_exp@example.com",
        )
        self.editor_group = Group.objects.create(name="Editor")
        self.editor = User.objects.create_user(username="editor_exp", password="test-password")
        self.editor.groups.add(self.editor_group)

        self.visitor = User.objects.create_user(username="visitor_exp", password="test-password")

        self.experience = Experience.objects.create(
            title="Staf Dokumentasi",
            organisation="COMPFEST",
            category="volunteer",
            description="Dokumentasi acara IT tahunan Fasilkom UI.",
            started_at="2025-03-01T00:00:00Z",
            ended_at="2025-10-01T00:00:00Z",
        )
        self.list_url = reverse("api:experience-list")
        self.detail_url = reverse("api:experience-detail", args=[self.experience.id])
        self.star_url = reverse("api:experience-star", args=[self.experience.id])
        self.payload = {
            "title": "Software Engineering Intern",
            "organisation": "Tech Company",
            "category": "internship",
            "description": "Developed backend microservices using Django REST framework.",
            "started_at": "2026-06-01T00:00:00Z",
            "ended_at": "2026-09-01T00:00:00Z",
            "thumbnail": "https://example.com/logo.png",
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.experience.id)) # type: ignore
        self.assertFalse(response.data[0]["is_starred"]) # type: ignore
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": "Dokumentasi"})
        self.assertEqual(len(response.data), 1) # type: ignore
        response = self.client.get(self.list_url, {"title": "NonExistentTitle"})
        self.assertEqual(response.data, []) # type: ignore

    def test_missing_experience_returns_404(self):
        url = reverse("api:experience-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user) # type: ignore
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "Hacked"}, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)

        self.assertEqual(Experience.objects.count(), 1)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Staf Dokumentasi")

    def test_editor_can_patch_and_put_but_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor) # type: ignore

        # Editor cannot create
        post_resp = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(post_resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Experience.objects.count(), 1)

        # Editor cannot delete
        del_resp = self.client.delete(self.detail_url)
        self.assertEqual(del_resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Experience.objects.count(), 1)

        # Editor can PATCH
        patch_resp = self.client.patch(self.detail_url, {"title": "Koordinator Dokumentasi"}, format="json")
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Koordinator Dokumentasi")

    def test_owner_can_create_and_delete(self):
        self.client.force_authenticate(user=self.owner) # type: ignore

        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Experience.objects.count(), 2)

        created_id = response.data["id"] # type: ignore
        detail_url = reverse("api:experience-detail", args=[created_id])

        del_resp = self.client.delete(detail_url)
        self.assertEqual(del_resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Experience.objects.count(), 1)

    def test_validation_rejects_empty_or_xss_tags(self):
        self.client.force_authenticate(user=self.owner) # type: ignore
        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"ended_at": "2020-01-01T00:00:00Z", "started_at": "2026-01-01T00:00:00Z"}, "ended_at"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data) # type: ignore
        self.assertEqual(Experience.objects.count(), 1)

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.visitor) # type: ignore
        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_starred"]) # type: ignore
        self.assertEqual(response.data["star_count"], 1) # type: ignore

        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_starred"]) # type: ignore
        self.assertEqual(response.data["star_count"], 0) # type: ignore

    def test_csrf_protection_enforced(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner_exp", password="test-password"))

        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) # type: ignore
        self.assertEqual(Experience.objects.count(), 1)

        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        token = client.cookies["csrftoken"].value
        response = client.post(self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED) # type: ignore
        self.assertEqual(Experience.objects.count(), 2)


class CreativeProjectAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner_port", password="test-password", email="owner_port@example.com",
        )
        self.editor_group = Group.objects.create(name="Editor")
        self.editor = User.objects.create_user(username="editor_port", password="test-password")
        self.editor.groups.add(self.editor_group)

        self.visitor = User.objects.create_user(username="visitor_port", password="test-password")

        self.project = CreativeProject.objects.create(
            title="Fotografi Comic Frontier",
            description="Dokumentasi acara Comifuro.",
            started_at="2025-05-01",
            ended_at="2025-05-03",
        )
        self.list_url = reverse("api:portfolio-list")
        self.detail_url = reverse("api:portfolio-detail", args=[self.project.id])
        self.star_url = reverse("api:portfolio-star", args=[self.project.id])
        self.payload = {
            "title": "Dokumentasi Wisuda UI",
            "description": "Foto kelulusan mahasiswa Fasilkom UI.",
            "started_at": "2026-08-20",
            "ended_at": "2026-08-22",
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.project.id)) # type: ignore
        self.assertFalse(response.data[0]["is_starred"]) # type: ignore
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": "Comic"})
        self.assertEqual(len(response.data), 1) # type: ignore
        response = self.client.get(self.list_url, {"title": "NonExistentKarya"})
        self.assertEqual(response.data, []) # type: ignore

    def test_missing_creative_project_returns_404(self):
        url = reverse("api:portfolio-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user) # type: ignore
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "Hacked"}, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)

        self.assertEqual(CreativeProject.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Fotografi Comic Frontier")

    def test_editor_can_patch_and_put_but_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor) # type: ignore

        # Editor cannot create
        post_resp = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(post_resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CreativeProject.objects.count(), 1)

        # Editor cannot delete
        del_resp = self.client.delete(self.detail_url)
        self.assertEqual(del_resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CreativeProject.objects.count(), 1)

        # Editor can PATCH
        patch_resp = self.client.patch(self.detail_url, {"title": "Fotografi Comic Frontier 18"}, format="json")
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Fotografi Comic Frontier 18")

    def test_owner_can_create_and_delete(self):
        self.client.force_authenticate(user=self.owner) # type: ignore

        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CreativeProject.objects.count(), 2)

        created_id = response.data["id"] # type: ignore
        detail_url = reverse("api:portfolio-detail", args=[created_id])

        del_resp = self.client.delete(detail_url)
        self.assertEqual(del_resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CreativeProject.objects.count(), 1)

    def test_validation_rejects_empty_or_xss_tags(self):
        self.client.force_authenticate(user=self.owner) # type: ignore
        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<iframe src="evil.com"></iframe>'}, "title"),
            ({"ended_at": "2020-01-01", "started_at": "2026-01-01"}, "ended_at"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data) # type: ignore
        self.assertEqual(CreativeProject.objects.count(), 1)

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.visitor) # type: ignore
        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_starred"]) # type: ignore
        self.assertEqual(response.data["star_count"], 1) # type: ignore

        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_starred"]) # type: ignore
        self.assertEqual(response.data["star_count"], 0) # type: ignore

    def test_csrf_protection_enforced(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner_port", password="test-password"))

        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) # type: ignore
        self.assertEqual(CreativeProject.objects.count(), 1)

        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        token = client.cookies["csrftoken"].value
        response = client.post(self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED) # type: ignore
        self.assertEqual(CreativeProject.objects.count(), 2)