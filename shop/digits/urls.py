from django.urls import path

from .views import (
    ProductDetailView,
    CategoryDetailView,
    BaseView,
    CartView,
    AddToCartView,
    DeleteFormCartView,
    ChangeCollView,
    CheckOutView,
    MakeOrderView,)

urlpatterns = [
    path('', BaseView.as_view(), name='index'),
    path('products/<str:ct_model>/<str:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('category/<str:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('cart/', CartView.as_view(), name='cart'),
    path('add-to-cart/<str:ct_model>/<str:slug>/', AddToCartView.as_view(), name='add_to_cart'),
    path('remove-from-cart/<str:ct_model>/<str:slug>/', DeleteFormCartView.as_view(), name='remove_from_cart'),
    path('change-coll_in-cart/<str:ct_model>/<str:slug>/', ChangeCollView.as_view(), name='change_coll_in_cart'),
    path('checkout/', CheckOutView.as_view(), name='check_out'),
    path('make-order/', MakeOrderView.as_view(), name='make_order')
]

