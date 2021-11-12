from django.urls import path

from digits.views import ProductDetailView

urlpatterns = [
    path('products/<str:ct_model>/<str:slug>/', ProductDetailView.as_view(), name='product_detail')
]

