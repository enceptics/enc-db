from dj_rest_auth.registration.views import (
    ResendEmailVerificationView,
    VerifyEmailView,
    RegisterView,
)

from django.contrib.auth import views as auth_views


from dj_rest_auth.views import (
    PasswordResetConfirmView,
    PasswordResetView,
    LoginView,
    LogoutView,
    UserDetailsView,
)
from authentication.views import email_confirm_redirect, booking_failure, booking_success,  PasswordResetRequestView, PasswordResetConfirmView, contact_us, notify_managers
from authentication.views import GetUserRole
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Assuming you have UserViewSet and CustomUserDetailsView in your views module
from .views import CheckoutView, CheckedInView, PaypalPaymentView, PaypalValidatePaymentView

from accounts.views import UserViewSet, CustomUserDetailsView
from accounts.views import CustomRegisterView, CustomLoginView, google_login

from authentication import views as auth_views

# Create a router instance
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # Booking
    path('checkout/', CheckoutView.as_view(), name="checkout"),
    path('get_current_checked_in_rooms/', CheckedInView.as_view(), name="checked_in_rooms"),

    # Authentication
    path('register/', CustomRegisterView.as_view(), name='custom-register'),
    path('login/', CustomLoginView.as_view(), name='custom-login'),

    # Google registration
    path('register/google/', include('social_django.urls', namespace='social')),
    path('google-login/', google_login, name='google-login'),

    path("logout/", LogoutView.as_view(), name="rest_logout"),
    path("user/", UserDetailsView.as_view(), name="rest_user_details"),
    path('api/user/role/', GetUserRole.as_view(), name='get_user_role'),
    path('api/user/update/', CustomUserDetailsView.as_view(), name='user_update'),

    path("register/verify-email/", VerifyEmailView.as_view(), name="rest_verify_email"),
    path("register/resend-email/", ResendEmailVerificationView.as_view(), name="rest_resend_email"),
    path("account-confirm-email/<str:key>/", email_confirm_redirect, name="account_confirm_email"),
    path("account-confirm-email/", VerifyEmailView.as_view(), name="account_email_verification_sent"),
    #  path("password/reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    # path(
    #     "password/reset/confirm/<uidb64>/<token>/",
    #     CustomPasswordResetConfirmView.as_view(),
    #     name="password_reset_confirm",
    # ),
    # path(
    #     "password/reset/redirect/<uidb64>/<token>/",
    #     password_reset_confirm_redirect,
    #     name="password_reset_confirm_redirect",
    # ),
    # path("password/reset/", PasswordResetView.as_view(), name="password_reset"),
    # path("password/reset/confirm/<str:uidb64>/<str:token>/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),

    # path("password/reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    # path("password/reset/confirm/<str:uidb64>/<str:token>/", CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),

    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password/reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # Payment
    path('booking/success/', booking_success, name='booking_success'),
    path('booking/failure/', booking_failure, name='booking_failure'),

    # PayPal
    path('paypal/create/', PaypalPaymentView.as_view(), name='ordercreate'),
    path('paypal/validate/', PaypalValidatePaymentView.as_view(), name='paypalvalidate'),

    # Pesapal
    path('pesapal/payment/', auth_views.PesapalPaymentAPIView.as_view(), name='pesapal_payment'),
    path('pesapal/transaction-status/', auth_views.PesapalTransactionStatusAPIView.as_view(), name='pesapal_transaction_status'),
    path('pesapal/ipn/', auth_views.pesapal_ipn, name='pesapal_ipn'),

    # Include the router URLs for UserViewSet
    path('api/', include(router.urls)),

    # CONTACT US
    path('contact-us/create/', contact_us, name='contact-us'),

    # Custom itenerary notify managers
    path("notify-managers/", notify_managers, name="notify_managers"),

    # cONTRACT
    path('contract/', auth_views.ContractDetailView.as_view(), name='contract-detail'),
    path('contract/sign/', auth_views.SignContractView.as_view(), name='contract-sign'),
    path('contract/download/', auth_views.DownloadContractView.as_view(), name='contract-download'),


]
