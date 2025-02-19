
from django.contrib import admin
from django.urls import path, include

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.conf import settings
from django.conf.urls.static import static

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from blog_posts.views import BlogPostViewSet, LikeViewSet, CommentViewSet, FollowerViewSet, BlogViewSet, SubscriptionViewSet
from accounts.views import ProfileViewSet
from accounts.views import Profile, User, CustomRegisterView, UserViewSet, CustomUserDetailsView, CustomSignupView
from authentication.views import PlaceViewset, PlaceInfoViewset, BookingViewSet, ReviewViewSet,ManagerPlaceViewset, HeroSectionView
from authentication import views

router = DefaultRouter()
router.register(r'blogposts', BlogPostViewSet)
router.register(r'users', UserViewSet)
router.register(r'profile', ProfileViewSet)
router.register(r'places', PlaceViewset)
router.register(r'place-info', PlaceInfoViewset)
router.register(r'book-place', BookingViewSet)
router.register(r'likes', LikeViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'followers', FollowerViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'manager/places', ManagerPlaceViewset, basename='manager-places') 
router.register(r'hero', HeroSectionView, basename='hero-section')
router.register(r'blogs', BlogViewSet)
router.register(r'subscriptions', SubscriptionViewSet)

schema_view = get_schema_view(
   openapi.Info(
      title="Enceptics APIs",
      default_version='v2',
      description="Test description",
      contact=openapi.Contact(email="owillypascal@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [

    path('weather/', include('weather.urls')),  # Include the weather app's URLs

    # Payments
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/auth/', include('authentication.urls')),
    path('api/', include(router.urls)),
    path('profile/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
]

# Only add this when we are in debug mode.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
document_root=settings.MEDIA_ROOT)


