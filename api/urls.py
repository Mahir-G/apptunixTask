from django.urls import path
from . import views
from rest_framework.authtoken import views as tokenviews

urlpatterns = [
    path('register', views.UserCreate.as_view(), name='create-user'),
    path('login', tokenviews.obtain_auth_token, name='get-token'),
    path('items', views.FoodCreate.as_view(), name="food-list-add"),
    path('items/<int:foodId>', views.FoodItemUpdate.as_view(), name="food-item-update"),
    path('cart', views.CartView.as_view(), name="cart"),
    path('orders', views.OrdersView.as_view(), name="orders"),
    path('rate', views.RateView.as_view(), name="rate"),
    path('change-state', views.ChangeStatusView.as_view(), name="change-status")
]