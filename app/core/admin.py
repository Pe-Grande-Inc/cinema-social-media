from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core import models


@admin.register(models.User)
class UserAdmin(UserAdmin):
    pass


admin.site.register(models.Post)
admin.site.register(models.PostRating)
admin.site.register(models.Comment)
admin.site.register(models.Genre)
admin.site.register(models.Title)
