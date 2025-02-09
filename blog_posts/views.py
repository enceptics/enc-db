from rest_framework import viewsets, status, filters, permissions
from .models import BlogPost, Like, Comment, Follower, Blogs
from .serializers import BlogPostSerializer, LikeSerializer, CommentSerializer, FollowerSerializer, BlogsSerializer
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
import logging

logger = logging.getLogger(__name__)

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only the author of a blog post to edit or delete it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all().order_by('-created_at')
    serializer_class = BlogPostSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['author__username', 'content']

    @action(detail=False, methods=['GET'])
    def search(self, request):
        query = request.query_params.get('query', '')
        results = BlogPost.objects.filter(
            Q(author__username__icontains=query) | Q(content__icontains=query)
        ).order_by('-created_at')
        serializer = BlogPostSerializer(results, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def like(self, request, pk=None):
        blog_post = self.get_object()
        user = request.user
        like, created = Like.objects.get_or_create(user=user, post=blog_post)
        if not created:
            like.delete()
            return Response({'status': 'unliked'}, status=status.HTTP_200_OK)
        return Response({'status': 'liked'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'])
    def like_count(self, request, pk=None):
        blog_post = self.get_object()
        return Response({'like_count': Like.objects.filter(post=blog_post).count()}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        # Remove the 'author' from the data before passing it to the serializer
        data = request.data.copy()  # If using FormData, you need to copy it
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=user)  # Automatically associate the logged-in user as the author

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all().order_by('-id')
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        post_id = request.data.get('post')
        user = request.user
        existing_like = Like.objects.filter(post_id=post_id, user=user).first()

        if existing_like:
            # If the user already liked the post, unlike it (delete the like)
            existing_like.delete()
            return Response({'status': 'unliked'}, status=status.HTTP_200_OK)
        else:
            # If the user has not liked the post yet, like it (create a new like)
            serializer = self.get_serializer(data={'post': post_id, 'user': user.pk})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-id')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class FollowerViewSet(viewsets.ModelViewSet):
    queryset = Follower.objects.all().order_by('-id')
    serializer_class = FollowerSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user_to_follow_id = request.data.get('follower')
        user = request.user
        existing_follow = Follower.objects.filter(user=user, follower_id=user_to_follow_id).exists()
        if existing_follow:
            return Response({'detail': 'You are already following this user.'}, status=status.HTTP_409_CONFLICT)
        serializer = self.get_serializer(data={'user': user.pk, 'follower': user_to_follow_id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# BLOGS
# ViewSet for BlogPost API
class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blogs.objects.all().order_by('-created_at')
    serializer_class = BlogsSerializer