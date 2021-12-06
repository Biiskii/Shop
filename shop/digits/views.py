from urllib import request
from django.views.generic import ListView
from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, View, CreateView
from .models import Notebook, Smartphone, Category, LatestProducts, Product, Fridge, Hob
from .mixins import CategoryDetailMixin
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from .forms import RegisterUserForm, LoginUserForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


class BaseView(ListView):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_left_sidebar()
        products = LatestProducts.objects.get_products_for_models(
            'notebook', 'smartphone', 'fridge', 'hob', with_respect_to='smartphone')

        if 'page' in request.GET:
            page = request.GET['page']
        else:
            page = 1
        paginator = Paginator(products, 3)
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        user_name = request.user
        context = {
            'categories': categories,
            'products': products,
            'user': user_name,
        }
        return render(request, 'base.html', context)





class ProductDetailView(CategoryDetailMixin, DetailView):
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
        return context


class CategoryDetailView(CategoryDetailMixin, DetailView):
    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'category_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'register.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return HttpResponseRedirect('/')


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'login.html'

    def get_success_url(self):
        return reverse_lazy('index')


def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')
