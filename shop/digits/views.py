from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, View, CreateView
from .models import Notebook, Smartphone, Category, LatestProducts, Customer, Cart, CartProduct, Product, Fridge, Hob
from .mixins import CategoryDetailMixin, CartMixin
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from .forms import OrderForm, RegisterUserForm, LoginUserForm
from .util import recalculate_cart


class BaseView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_left_sidebar()
        products = LatestProducts.objects.get_products_for_models(
            'notebook', 'smartphone', 'fridge', 'hob', with_respect_to='smartphone')
        context = {
            'categories': categories,
            'products': products,
            'cart': self.cart,
        }
        return render(request, 'base.html', context)


class ProductDetailView(CartMixin, CategoryDetailMixin, DetailView):
    CT_MODEL_MODEL_CLASS = {
        'notebook': Notebook,
        'smartphone': Smartphone,
        'fridge': Fridge,
        'hob': Hob,
    }

    def dispatch(self, request, *args, **kwargs):
        self.model = self.CT_MODEL_MODEL_CLASS[kwargs['ct_model']]
        self.queryset = self.model._base_manager.all()
        return super().dispatch(request, *args, **kwargs)

    context_object_name = 'product'
    template_name = 'product_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ct_model'] = self.model._meta.model_name
        context['cart'] = self.cart
        return context


class CategoryDetailView(CartMixin, CategoryDetailMixin, DetailView):
    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'category_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart
        return context


class AddToCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product, created = CartProduct.objects.get_or_create(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id)
        if created:
            self.cart.products.add(cart_product)
        recalculate_cart(self.cart)
        messages.add_message(request, messages.INFO, "Товар ({}) добавлен в корзину".format(product.title))
        return HttpResponseRedirect('/cart/')


class DeleteFormCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id)
        self.cart.products.remove(cart_product)
        cart_product.delete()
        recalculate_cart(self.cart)
        messages.add_message(request, messages.INFO, "Товар ({}) удален из корзины".format(product.title))
        return HttpResponseRedirect('/cart/')


class ChangeCollView(CartMixin, View):

    def post(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id)
        coll = int(request.POST.get('coll'))
        cart_product.coll = coll
        cart_product.save()
        recalculate_cart(self.cart)
        messages.add_message(request, messages.INFO,
                             "Количество товара ({}) изменено на ({})".format(product.title, str(coll)))
        return HttpResponseRedirect('/cart/')


class CartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_left_sidebar()
        context = {
            'cart': self.cart,
            'categories': categories,
        }
        return render(request, 'cart.html', context)


class CheckOutView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_left_sidebar()
        form = OrderForm(request.POST or None)
        context = {
            'form': form,
            'cart': self.cart,
            'categories': categories,
        }
        return render(request, 'checkout.html', context)


class MakeOrderView(CartMixin, View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        customer = Customer.objects.get(user=request.user)
        if form.is_valid():
            new_order = form.save(commit=False)
            new_order.customer = customer
            new_order.first_name = form.cleaned_data['first_name']
            new_order.last_name = form.cleaned_data['last_name']
            new_order.phone = form.cleaned_data['phone']
            new_order.address = form.cleaned_data['address']
            new_order.buying = form.cleaned_data['buying']
            new_order.order_date = form.cleaned_data['order_date']
            new_order.comment = form.cleaned_data['comment']
            new_order.save()
            self.cart.in_order = True
            self.cart.save()
            new_order.cart = self.cart
            new_order.save()
            customer.orders.add(new_order)
            messages.add_message(request, messages.INFO, 'Спасибо за заказ')
            return HttpResponseRedirect('/')
        return HttpResponseRedirect('checkout/')


class RegisterUser(CartMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'register.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return HttpResponseRedirect('/')


class LoginUser(CartMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'login.html'

    def get_success_url(self):
        return reverse_lazy('index')


def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')
