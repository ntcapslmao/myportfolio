from django.contrib import admin

# Register your models here.
from .models import Experience, Education

admin.site.register(Experience)
admin.site.register(Education)