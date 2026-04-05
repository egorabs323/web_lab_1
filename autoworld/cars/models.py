from django.db import models
from django.urls import reverse


class PublishedCarManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=1)


class CarCategory(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name="Категория")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('cars:category', kwargs={'cat_slug': self.slug})

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']


class CarTag(models.Model):
    tag = models.CharField(max_length=100, db_index=True, verbose_name="Тег")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    def __str__(self):
        return self.tag

    def get_absolute_url(self):
        return reverse('cars:tag', kwargs={'tag_slug': self.slug})

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class CarEngine(models.Model):
    engine_type = models.CharField(max_length=50, verbose_name="Тип двигателя")
    displacement = models.DecimalField(max_digits=4, decimal_places=1, verbose_name="Объем (л)")
    horsepower = models.IntegerField(verbose_name="Мощность (л.с.)")

    def __str__(self):
        return f"{self.engine_type} {self.displacement}L ({self.horsepower} л.с.)"

    class Meta:
        verbose_name = "Двигатель"
        verbose_name_plural = "Двигатели"


class Car(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'

    title = models.CharField(max_length=255, verbose_name="Название")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    brand = models.CharField(max_length=100, verbose_name="Марка")
    model_name = models.CharField(max_length=100, verbose_name="Модель")
    year = models.IntegerField(verbose_name="Год выпуска")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    body_type = models.CharField(max_length=50, verbose_name="Тип кузова")
    vin = models.CharField(max_length=17, unique=True, verbose_name="VIN-код")
    description = models.TextField(blank=True, verbose_name="Описание")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время изменения")
    is_published = models.BooleanField(
        choices=Status.choices,
        default=Status.PUBLISHED,
        verbose_name="Публикация"
    )

    category = models.ForeignKey('CarCategory', on_delete=models.PROTECT,
                                 related_name='cars', verbose_name="Категория")
    tags = models.ManyToManyField('CarTag', blank=True, related_name='cars', verbose_name="Теги")
    engine = models.OneToOneField('CarEngine', on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='car', verbose_name="Двигатель")

    objects = models.Manager()
    published = PublishedCarManager()

    class Meta:
        ordering = ['-time_create']
        indexes = [
            models.Index(fields=['-time_create']),
            models.Index(fields=['slug']),
            models.Index(fields=['brand']),
        ]
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'

    def __str__(self):
        return f"{self.brand} {self.model_name} ({self.year})"

    def get_absolute_url(self):
        return reverse('cars:car_detail', kwargs={'car_slug': self.slug})