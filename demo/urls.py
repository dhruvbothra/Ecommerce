from django.contrib import admin
from django.urls import path,include
from . import views


urlpatterns = [
    path("",views.products,name="products"),
    path('accounts/', include('allauth.urls')),
    path('male/',views.maleproducts,name="maleproducts"),
    path('female/',views.femaleproducts,name="femaleproducts"),
    path('kids/',views.kidsproducts,name="kidsproducts"),
    path('add_to_cart/<int:id>/',views.add_to_cart,name="add_to_cart"),
    path('remove_from_cart/<int:id>/',views.remove_from_cart,name="remove_from_cart"),
    path('remove_one_item_from_cart/<int:id>/',views.remove_one_item_from_cart,name="remove_one_item_from_cart"),
    path('ordersummary/',views.OrderSummaryView.as_view(),name="ordersummary"),
    path('checkout/',views.checkout.as_view(),name="checkout"),
    path('payment/<payment_option>/',views.PaymentView.as_view(), name="payment")
] 

