from django.contrib import admin
from .models import Category,Tag,Post,Like,Comment,Share,Bookmark
# Register your models here.
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Share)
admin.site.register(Bookmark)

