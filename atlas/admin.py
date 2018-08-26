from django.contrib import admin

from atlas import models


class DomainIdInline(admin.TabularInline):
    model = models.DomainId


class LanguageNameInline(admin.TabularInline):
    model = models.LanguageName


@admin.register(models.Entity)
class EntityAdmin(admin.ModelAdmin):
    inlines = [
        DomainIdInline,
        LanguageNameInline,
    ]
