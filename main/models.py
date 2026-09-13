import uuid
from django.db import models

class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ('internship', 'Internship'),
        ('research', 'Research'),
        ('volunteer', 'Volunteer'),
        ('part-time', 'Part-Time'),
        ('full-time', 'Full-Time'),
        ('freelance', 'Freelance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    organisation = models.CharField(max_length=255, default="Personal")
    description = models.TextField()
    category = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='full-time')
    thumbnail = models.URLField(blank=True, null=True)

    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return self.title
    
    @property
    def is_ongoing(self):
        return self.ended_at is None

class Education(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    started_at = models.DateField()
    ended_at = models.DateField(blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.degree} at {self.institution}"

    @property
    def is_ongoing(self):
        return self.ended_at is None

class CreativeProject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    started_at = models.DateField()
    ended_at = models.DateField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
        
    @property
    def is_ongoing(self):
        return self.ended_at is None

class PortfolioItem(models.Model):
    project = models.ForeignKey(CreativeProject, related_name='items', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, help_text="Used for image alt text")
    image_url = models.CharField(max_length=500, blank=True, null=True, help_text="Imgur link or /static/img/ path")
    video_embed_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.title} (in {self.project.title})"