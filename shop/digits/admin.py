from PIL import Image
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from .models import *
from django.forms import ModelChoiceField, ModelForm


class NotebookAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].help_text = mark_safe('<span style="color:red; font-size:14px;">Загружайте картинки '
                                                   'размером '
                                                   'более чем {}*{}, но не более{}*{} и "весом" до 3 Мб</span>'.format(
            *Product.VALID_RESOLUTION_MIN, *Product.VALID_RESOLUTION_MAX))

    def clean_image(self):
        image = self.cleaned_data['image']
        img = Image.open(image)
        min_width, min_height = Product.VALID_RESOLUTION_MIN
        max_width, max_height = Product.VALID_RESOLUTION_MAX
#        if image.size > Product.MAX_IMAGE_SIZE:
#            raise ValidationError('Объем загружаемое изображение ({}) больше допустимого'.format(image.size))
        if img.width < min_width or img.height < min_height:
            raise ValidationError('Загружаемое изображение ({}*{}) меньше допустимого'.format(img.width, img.height))
        if img.width > max_width or img.height > max_height:
            raise ValidationError('Загружаемое изображение ({}*{}) больше допустимого'.format(img.width, img.height))
        return image


class NotebookAdmin(admin.ModelAdmin):
    form = NotebookAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='notebooks'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SmartphoneAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='smartphone'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class FridgeAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='fridge'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class HobAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='hob'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Order)
admin.site.register(Category)
admin.site.register(Notebook, NotebookAdmin)
admin.site.register(Smartphone, SmartphoneAdmin)
admin.site.register(Fridge, FridgeAdmin)
admin.site.register(Hob, HobAdmin)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Customer)
