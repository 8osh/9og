from django.contrib import admin
from .models import Post, Comment, Category
# Register your models here.

class PostAdmin(admin.ModelAdmin):
    list_display        = ['title', 'created_on', 'edited_on', 'slug']
    list_display_links  = ['title', 'created_on']
    list_filter         = ['title', 'created_on']
    search_fields       = ['title', 'content']

    class Meta:
        model = Post


admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
admin.site.register(Category)