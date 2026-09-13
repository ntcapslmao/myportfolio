from django.contrib import admin

# Register your models here.
from .models import Experience, Education, CreativeProject, PortfolioItem

admin.site.register(Experience)
admin.site.register(Education)

class PortfolioItemInline(admin.TabularInline):
    model = PortfolioItem
    extra = 3

@admin.register(CreativeProject)
class CreativeProjectAdmin(admin.ModelAdmin):
    inlines = [PortfolioItemInline]