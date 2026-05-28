import os
import uuid
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.db.models import Q, F, Value, Count, Avg, Max, Min
from django.db.models.functions import Length
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    FormView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .forms import AddCarForm, AddCarModelForm, UploadFileForm
from .models import Car, CarCategory, CarTag


class DataMixin:
    paginate_by = 2
    title_page = None
    context_object_name = 'cars'
    extra_context = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        extra_context = self.extra_context.copy()
        if self.title_page:
            extra_context['title'] = self.title_page
        self.extra_context = extra_context

    def get_mixin_context(self, context, **kwargs):
        if self.title_page:
            context['title'] = self.title_page
        context.update(kwargs)
        return context


class CarsHome(DataMixin, ListView):
    template_name = 'cars/index.html'
    title_page = 'Главная страница'

    def get_queryset(self):
        return Car.published.select_related('category', 'engine').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stats = Car.published.aggregate(
            avg_price=Avg('price'),
            max_year=Max('year'),
            min_price=Min('price'),
            total_cars=Count('id')
        )
        return self.get_mixin_context(
            context,
            cars_q=Car.published.filter(Q(brand__icontains='toyota') | Q(year__gte=2025)),
            cars_f=Car.published.filter(price__gt=F('year') * 100),
            cars_annotated=Car.published.annotate(
                title_len=Length('title'),
                is_new=Value(True)
            ).order_by('-price')[:5],
            cars_values=Car.published.values('brand', 'model_name', 'price', 'category__name')[:5],
            stats=stats,
            categories_with_count=CarCategory.objects.annotate(cars_count=Count('cars')).filter(cars_count__gt=0),
            first_car=Car.published.first(),
            last_car=Car.published.order_by('-year').last(),
            has_suv_tag=CarTag.objects.filter(slug='suv').exists(),
            total_published=Car.published.count(),
        )


class AddCarPage(DataMixin, View):
    title_page = 'Добавить автомобиль'
    template_name = 'cars/add_car.html'

    def get(self, request):
        form = AddCarForm()
        return self.render_form(request, form)

    def post(self, request):
        form = AddCarForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                if 'file_upload' in request.FILES:
                    handle_uploaded_file(request.FILES['file_upload'])
                return redirect('cars:index')
            except Exception as e:
                form.add_error(None, f"Ошибка добавления: {e}")
        return self.render_form(request, form)

    def render_form(self, request, form):
        context = self.get_mixin_context({
            'form': form,
            'form_type': 'unbound',
        })
        return render(request, self.template_name, context)


class AddCarModelPage(DataMixin, CreateView):
    form_class = AddCarModelForm
    template_name = 'cars/add_car.html'
    success_url = reverse_lazy('cars:index')
    title_page = 'Добавить автомобиль (модель)'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, form_type='model')


class UpdateCarPage(DataMixin, UpdateView):
    model = Car
    form_class = AddCarModelForm
    template_name = 'cars/add_car.html'
    slug_url_kwarg = 'car_slug'
    title_page = 'Редактирование автомобиля'

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, form_type='model')


class DeleteCarPage(DataMixin, DeleteView):
    model = Car
    template_name = 'cars/car_confirm_delete.html'
    slug_url_kwarg = 'car_slug'
    success_url = reverse_lazy('cars:cars_list')
    title_page = 'Удаление автомобиля'


class UploadFilePage(DataMixin, FormView):
    form_class = UploadFileForm
    template_name = 'cars/upload_file.html'
    title_page = 'Загрузить файл'

    def form_valid(self, form):
        filepath = handle_uploaded_file(form.cleaned_data['file'])
        return self.render_to_response(self.get_context_data(
            form=form,
            filepath=filepath,
            uploaded=True,
            title='Файл загружен'
        ))


class CarDetailPage(DataMixin, DetailView):
    model = Car
    template_name = 'cars/car_detail.html'
    context_object_name = 'car'
    slug_url_kwarg = 'car_slug'

    def get_queryset(self):
        return Car.published.select_related('category', 'engine').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title=f'{self.object.brand} {self.object.model_name}')


class CarsListPage(DataMixin, ListView):
    template_name = 'cars/cars_list.html'
    title_page = 'Список всех автомобилей'

    def get_queryset(self):
        min_year = self.request.GET.get('min_year')
        max_price = self.request.GET.get('max_price')
        body_type = self.request.GET.get('body_type')

        cars = Car.published.all()

        if min_year:
            try:
                cars = cars.filter(year__gte=int(min_year))
            except (ValueError, TypeError):
                pass
        if max_price:
            try:
                cars = cars.filter(price__lte=Decimal(max_price))
            except (ValueError, TypeError, InvalidOperation):
                pass
        if body_type:
            cars = cars.filter(body_type=body_type)

        return cars

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        min_year = self.request.GET.get('min_year')
        max_price = self.request.GET.get('max_price')
        body_type = self.request.GET.get('body_type')
        return self.get_mixin_context(
            context,
            brands=Car.objects.values_list('brand', flat=True).distinct().order_by('brand'),
            body_types=Car.objects.values_list('body_type', flat=True).distinct().order_by('body_type'),
            filter_info={
                'min_year': min_year or 'не указан',
                'max_price': max_price or 'не указана',
                'body_type': body_type or 'не указан'
            }
        )


class CategoryCarsPage(DataMixin, ListView):
    template_name = 'cars/index.html'

    def get_queryset(self):
        self.category = get_object_or_404(CarCategory, slug=self.kwargs['cat_slug'])
        return Car.published.filter(category=self.category).select_related('category', 'engine').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(
            context,
            title=f'Категория: {self.category.name}',
            cat_selected=self.category.pk
        )


class TagCarsPage(DataMixin, ListView):
    template_name = 'cars/index.html'

    def get_queryset(self):
        self.tag = get_object_or_404(CarTag, slug=self.kwargs['tag_slug'])
        return self.tag.cars.filter(is_published=Car.Status.PUBLISHED).select_related('category', 'engine')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(
            context,
            title=f'Тег: {self.tag.tag}',
            tag_selected=self.tag.pk
        )


class BrandCarsPage(DataMixin, ListView):
    template_name = 'cars/brand.html'

    def get_queryset(self):
        self.brand_slug = self.kwargs['brand_slug'].lower()
        return Car.published.filter(brand__iexact=self.brand_slug)

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        if not self.object_list.exists():
            return redirect('cars:cars_list')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brand_name = self.object_list.first().brand
        return self.get_mixin_context(
            context,
            title=f'Автомобили марки {brand_name}',
            brand=brand_name,
            models=self.object_list.values_list('model_name', flat=True).distinct()
        )


class VinInfoPage(DataMixin, TemplateView):
    template_name = 'cars/vin.html'

    def get(self, request, *args, **kwargs):
        if not self.kwargs['vin_code'] or len(self.kwargs['vin_code']) != 17:
            return redirect('cars:cars_list')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vin_code = self.kwargs['vin_code']
        return self.get_mixin_context(
            context,
            title='Информация по VIN-коду',
            vin_code=vin_code,
            wmi=vin_code[:3],
            vds=vin_code[3:9],
            vis=vin_code[9:],
            car=Car.objects.filter(vin=vin_code).first(),
        )


class BrandsListPage(DataMixin, TemplateView):
    template_name = 'cars/brands_list.html'
    title_page = 'Все марки автомобилей'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brands = Car.objects.filter(is_published=1).values_list('brand', flat=True).distinct().order_by('brand')
        brands_data = []
        for brand in brands:
            brands_data.append({
                'name': brand.lower().replace(' ', '-'),
                'slug': brand.lower().replace(' ', '-'),
                'display': brand,
                'count': Car.objects.filter(brand=brand, is_published=1).count()
            })
        return self.get_mixin_context(context, brands=brands_data)


class CategoriesListPage(DataMixin, ListView):
    template_name = 'cars/categories_list.html'
    context_object_name = 'categories'
    title_page = 'Все категории'

    def get_queryset(self):
        return CarCategory.objects.annotate(cars_count=Count('cars')).filter(cars_count__gt=0).order_by('name')


class TagsListPage(DataMixin, ListView):
    template_name = 'cars/tags_list.html'
    context_object_name = 'tags'
    title_page = 'Все теги'

    def get_queryset(self):
        return CarTag.objects.annotate(cars_count=Count('cars')).filter(cars_count__gt=0).order_by('tag')


def handle_uploaded_file(f):
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
    os.makedirs(upload_dir, exist_ok=True)

    name = f.name
    ext = ''
    if '.' in name:
        ext = name[name.rindex('.'):]
        name = name[:name.rindex('.')]

    suffix = str(uuid.uuid4())
    filepath = os.path.join(upload_dir, f"{name}_{suffix}{ext}")

    with open(filepath, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return f"uploads/{name}_{suffix}{ext}"
