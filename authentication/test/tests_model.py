from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Profile, Post

User = get_user_model()

class BlogTests(TestCase):

    @classmethod

    def setUpTestData(cls):

    # Create a user
        testuser1 = User.objects.create_user(
        username='testuser1', password='abc123')
        testuser1.save()
        # Create a blog post
        test_post = Post.objects.create(
        author=testuser1, body='Body content...')
        test_post.save()
    def test_blog_content(self):
        post = Post.objects.get(id=1)
        author = f'{post.author}'
        body = f'{post.body}'
        self.assertEqual(author, 'testuser1')
        self.assertEqual(body, 'Body content...')




    



        