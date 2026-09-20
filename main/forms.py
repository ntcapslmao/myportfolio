from django import forms
from django.forms import ModelForm, TextInput, Textarea, URLInput, DateTimeInput, Select, DateInput
from django.conf import settings
from django.core.exceptions import ValidationError

from main.models import Project, Experience, Education, CreativeProject

class ExperienceForm(ModelForm):
    passcode = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Masukkan kata sandi",
                "style": "width: 100%; padding: 0.7rem; border: 1px solid var(--accent); border-radius: var(--radius); font: inherit; background: transparent; color: var(--ink);"
            }
        ),
        required=True,
        label="Admin Password"
    )

    class Meta:
        model = Experience
        fields = [
            "title",
            "organisation",
            "category",
            "description",
            "thumbnail",
            "started_at",
            "ended_at",
        ]

        labels = {
            "title": "Nama Posisi/Peran",
            "Organisation": "Nama Organisasi",
            "category": "Kategori Pengalaman",
            "description": "Deskripsi Pengalaman",
            "thumbnail": "URL Thumbnail (opsional)",
            "started_at": "Waktu Mulai",
            "ended_at": "Waktu Selesai (opsional)",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "e.g. Staff of Documentation",
                    "maxlength": 255
                    }
            ),
            "organisation": TextInput(
                attrs={
                    "placeholder": "e.g. BEM Fasilkom UI",
                    "maxlength": 255
                }
            ),
            "category": Select(
                attrs={
                    "class": "form-select"
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Jelaskan peran dan kontribusi...",
                    "rows": 4
                }
            ),
            "thumbnail": URLInput(
                attrs={
                    "placeholder": "e.g. https://github.com/..."
                }
            ),
            "started_at": DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-date"
                }
            ),
            "ended_at": DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-date"
                }
            )
        }

    def clean_passcode(self):
        data = self.cleaned_data.get("passcode")
        if data != settings.SECRET_PASSWORD:
            raise ValidationError("Access denied: Invalid Password!")
        return data

class EducationForm(ModelForm):
    passcode = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Masukkan kata sandi",
                "style": "width: 100%; padding: 0.7rem; border: 1px solid var(--accent); border-radius: var(--radius); font: inherit; background: transparent; color: var(--ink);"
            }
        ),
        required=True,
        label="Admin Password"
    )

    class Meta:
        model = Education
        fields = [
            "institution",
            "degree",
            "description",
            "started_at",
            "ended_at",
        ]

        labels = {
            "institution": "Nama Institusi",
            "degree": "Gelar/Jurusan",
            "description": "Deskripsi (opsional)",
            "started_at": "Tanggal Mulai",
            "ended_at": "Tanggal Selesai (opsional)",
        }

        widgets = {
            "institution": TextInput(
                attrs={
                    "placeholder": "e.g. Universitas Indonesia",
                    "maxlength": 255
                    }
            ),
            "degree": TextInput(
                attrs={
                    "placeholder": "e.g. Bachelor of Arts",
                    "maxlength": 255
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Jelaskan peran dan kontribusi...",
                    "rows": 4
                }
            ),
            "started_at": DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "ended_at": DateInput(
                attrs={
                    "type": "date",
                }
            )
        }

    def clean_passcode(self):
        data = self.cleaned_data.get("passcode")
        if data != settings.SECRET_PASSWORD:
            raise ValidationError("Access denied: Invalid Password!")
        return data

class ProjectForm(ModelForm):
    passcode = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Masukkan kata sandi",
                "style": "width: 100%; padding: 0.7rem; border: 1px solid var(--accent); border-radius: var(--radius); font: inherit; background: transparent; color: var(--ink);"
            }
        ),
        required=True,
        label="Admin Password"
    )

    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "tech_stack",
            "project_url",
            "project_image_url",
        ]

        labels = {
            "title": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "tech_stack": "Teknologi yang Digunakan",
            "project_url": "URL Proyek",
            "project_image_url": "URL Gambar Proyek",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Portfolio Website",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan Proyekmu",
                    "rows": 3,
                }
            ),
            "tech_stack": TextInput(
                attrs={
                    "placeholder": "Django, Python, HTML, CSS",
                }
            ),
            "project_url": URLInput(
                attrs={
                    "placeholder": "https://github.com/kakBurhan/burhanquestv4",
                }
            ),
            "project_image_url": URLInput(
                attrs={
                    "placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000",
                }
            ),
        }

    def clean_passcode(self):
        data = self.cleaned_data.get("passcode")
        if data != settings.SECRET_PASSWORD:
            raise ValidationError("Access denied: Invalid Password!")
        return data

class CreativeProjectForm(forms.ModelForm):
    passcode = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Masukkan kata sandi", 
                "style": "width: 100%; padding: 0.7rem; border: 1px solid var(--accent); border-radius: var(--radius); font: inherit; background: transparent; color: var(--ink);"
            }
        ),
        required=True,
        label="Admin Password"
    )

    class Meta:
        model = CreativeProject
        fields = ["title", "description", "started_at", "ended_at"]
        labels = {
            "title": "Nama Karya/Acara",
            "description": "Deskripsi Acara",
            "started_at": "Tanggal Mulai",
            "ended_at": "Tanggal Selesai (opsional)",
        }
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. Dokumentasi CF18"}),
            "description": forms.Textarea(attrs={"placeholder": "Ceritakan tentang karya/acara ini...", "rows": 4}),
            "started_at": forms.DateInput(attrs={"type": "date"}),
            "ended_at": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_passcode(self):
        data = self.cleaned_data.get("passcode")
        if data != settings.SECRET_PASSWORD:
            raise ValidationError("Access denied: Invalid Password!")
        return data