from django.contrib import admin

from .models import GithonFee

# Register your models here.

@admin.register(GithonFee)
class GithonFeeManager(admin.ModelAdmin):
    pass
