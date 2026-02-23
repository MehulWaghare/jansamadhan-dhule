from django.contrib import admin
from .models import Category, Complaint, Comment, Like


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'status', 'created_at']
    list_filter = ['status', 'category']
    search_fields = ['title', 'description', 'address']
    readonly_fields = ['latitude', 'longitude', 'address']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'complaint', 'created_at']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'complaint']