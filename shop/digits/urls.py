from django.urls import path

from .views import (
    ProductDetailView,
    CategoryDetailView,
    BaseView,
    RegisterUser,
    logout_user,
    LoginUser,
)

urlpatterns = [
    path('', BaseView.as_view(), name='index'),
    path('products/<str:ct_model>/<str:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('category/<str:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('register/', RegisterUser.as_view(), name='register'),
]

