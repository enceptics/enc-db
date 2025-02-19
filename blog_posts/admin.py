from django.contrib import admin
from .models import BlogPost, Like, Comment, Follower, Blogs, Subscription

# Blog posts

model_list = [BlogPost]
admin.site.register(model_list)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Follower)
admin.site.register(Blogs)
admin.site.register(Subscription)






