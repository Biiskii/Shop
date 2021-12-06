from django.views.generic.detail import SingleObjectMixin
from django.views.generic import View

from .models import (
    Category,
    Notebook,
    Smartphone,
    Fridge,
    Hob,
)


class CategoryDetailMixin(SingleObjectMixin):
    CATEGORY_SLUGPRODUCT_MODEL = {
        'notebooks': Notebook,
        'smartphone': Smartphone,
        'fridge': Fridge,
        'hob': Hob,
    }

    def get_context_data(self, **kwargs):
        if isinstance(self.get_object(), Category):
            model = self.CATEGORY_SLUGPRODUCT_MODEL[self.get_object().slug]
            context = super().get_context_data(**kwargs)
            context['categories'] = Category.objects.get_categories_for_left_sidebar()
            context['category_products'] = model.objects.all()
            return context
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.get_categories_for_left_sidebar()
        return context


