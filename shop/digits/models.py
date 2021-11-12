from PIL import Image
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse
User = get_user_model()


def get_product_url(obj, viewname):
    ct_model = obj.__cllas__._meta.model_name
    return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})


class MinResolutonErrorException(Exception):
    pass


class MaxResolutonErrorException(Exception):
    pass


class LatestProductsManager:

    @staticmethod
    def get_products_for_models(*args, **kwargs):
        with_respect_to = kwargs.get('with_respect_to')
        products = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:5]
            products.extend(model_products)
        if with_respect_to:
            ct_model = ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists():
                if with_respect_to in args:
                    return sorted(products, key=lambda x: x.__class__._meta.model_name.startswith(with_respect_to),
                                  reverse=True)
        return products


class LatestProducts:
    objects = LatestProductsManager()


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование товара')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    VALID_RESOLUTION_MIN = (400, 400)
    VALID_RESOLUTION_MAX = (1500, 1500)
    MAX_IMAGE_SIZE = 3145728

    class Meta:
        abstract = True

    category = models.ForeignKey(Category, verbose_name='категория', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='наименование товара')
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='изображение')
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')
    description = models.TextField(null=True, verbose_name='описание товара')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        image = self.image
        img = Image.open(image)
        min_width, min_height = self.VALID_RESOLUTION_MIN
        max_width, max_height = self.VALID_RESOLUTION_MAX
        if img.width < min_width or img.height < min_height:
            raise MinResolutonErrorException(
                'Загружаемое изображение ({}*{}) меньше допустимого'.format(img.width, img.height))
        if img.width > max_width or img.height > max_height:
            raise MaxResolutonErrorException(
                'Загружаемое изображение ({}*{}) больше допустимого'.format(img.width, img.height))
        super().save(*args, **kwargs)


class Notebook(Product):
    diagonal = models.CharField(max_length=255, verbose_name='Диагональ')
    display_type = models.CharField(max_length=255, verbose_name=' Тип дисплея')
    processor_frec = models.CharField(max_length=255, verbose_name='Частота процессора')
    ram = models.CharField(max_length=255, verbose_name='Оперативная память')
    video = models.CharField(max_length=255, verbose_name='Видеокарта')
    time_without_charge = models.CharField(max_length=255, verbose_name='Время работы акумулятора')

    def __str__(self):
        return '{} : {}'.format(self.category.name, self.title)

    def get_absolut_url(self):
        return get_product_url(self, 'product_detail')


class Smartphone(Product):
    diagonal = models.CharField(max_length=255, verbose_name='Диагональ')
    display_type = models.CharField(max_length=255, verbose_name=' Тип дисплея')
    resolution = models.CharField(max_length=255, verbose_name='Разрешение экрана')
    accum_volume = models.CharField(max_length=255, verbose_name='Емкость аккумулятора')
    ram = models.CharField(max_length=255, verbose_name='Оперативная память')
    sd = models.BooleanField(default=True, verbose_name='Поддержка sd карты')
    sd_volume = models.CharField(max_length=255, verbose_name='Максимальный объем sd карты')
    main_cam_mp = models.CharField(max_length=255, verbose_name='Основная камера')
    frontal_cam_mp = models.CharField(max_length=255, verbose_name='Фронтальная камера')

    def __str__(self):
        return '{} : {}'.format(self.category.name, self.title)

    def get_absolut_url(self):
        return get_product_url(self, 'product_detail')


class CartProduct(models.Model):
    user = models.ForeignKey('Customer', verbose_name='покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='карзина', on_delete=models.CASCADE, related_name='relates_products')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    coll = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Итоговая цена')

    def __str__(self):
        return 'Продукт {} (Для корзины)'.format(self.product.title)


class Cart(models.Model):
    owner = models.ForeignKey('Customer', verbose_name='Владелец', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Итоговая цена')

    def __str__(self):
        return str(self.id)


class Customer(models.Model):
    user = models.ForeignKey(User, verbose_name='пользователь', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')
    address = models.CharField(max_length=255, verbose_name='Адрес')

    def __str__(self):
        return 'Пукупатель: {} {}'.format(self.first_name, self.last_name)
