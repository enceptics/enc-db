from django.db import models
from django.conf import settings

class BlogPost(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts", null=True, blank=True)
    content = models.TextField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='blog_post_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.content[:30]} - {self.created_at.strftime('%d %b %Y')}"

    def author_full_name(self):
        if self.author.first_name and self.author.last_name:
            return f"{self.author.first_name} {self.author.last_name}"
        return self.author.username

    def author_current_city(self):
        return self.author.profile.current_city if hasattr(self.author, 'profile') else None

    def like_count(self):
        return self.likes.count()  # Counts likes dynamically

    def comment_count(self):
        return self.comments.count()  # Counts comments dynamically

class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="liked_posts")
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)  # Track when the like was made

    class Meta:
        unique_together = ('user', 'post')  # Prevents duplicate likes

    def __str__(self):
        return f"{self.user.username} likes {self.post.author.username}'s post"

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.text[:30]}"

class Follower(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following")
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followers")

    class Meta:
        unique_together = ('user', 'follower')  # Prevent duplicate follow entries

    def __str__(self):
        return f"{self.follower.username} follows {self.user.username}"


# BLOGPOSTS
class Blogs(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    subtitle = models.CharField(max_length=255, null=True, blank=True)  # Optional subtitle
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)  # Optional location
    reading_time = models.IntegerField(null=True, blank=True)  # Estimated time in minutes
    tags = models.CharField(max_length=255, null=True, blank=True)  # Comma-separated tags
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)  # Blog published date
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)  # Last updated date

    def __str__(self):
        return self.title if self.title else "Untitled Blog"




