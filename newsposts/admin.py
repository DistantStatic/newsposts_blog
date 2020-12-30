from django.contrib import admin

# Register your models here.
from .models import Newspost, Comment

admin.site.register(Newspost)
admin.site.register(Comment)