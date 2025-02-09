from django.urls import path

from . import views

urlpatterns = [

    path("daraja/", views.MpesaPaymentView.as_view(), name="mpesa-payments"),


    # path("checkout/", views.MpesaCheckout.as_view(), name="checkout"),
    # path("callback/", views.MpesaCallBack.as_view(), name="callback"),
]