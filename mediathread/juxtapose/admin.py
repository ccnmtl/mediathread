from django.contrib import admin
from mediathread.juxtapose.models import (
    JuxtaposeAsset, JuxtaposeMediaElement,
    JuxtaposeTextElement
)


@admin.register(JuxtaposeAsset)
class JuxtaposeAssetAdmin(admin.ModelAdmin):
    class Meta:
        model = JuxtaposeAsset


@admin.register(JuxtaposeMediaElement)
class JuxtaposeMediaElementAdmin(admin.ModelAdmin):
    class Meta:
        model = JuxtaposeMediaElement


@admin.register(JuxtaposeTextElement)
class JuxtaposeTextElementAdmin(admin.ModelAdmin):
    class Meta:
        model = JuxtaposeTextElement
