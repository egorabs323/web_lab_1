from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, F, Value, Count, Avg, Max, Min, Sum
from django.db.models.functions import Length
from .models import Car, CarCategory, CarTag
from decimal import Decimal, InvalidOperation
from .forms import AddCarForm, AddCarModelForm, UploadFileForm
import uuid
import os
from django.conf import settings

def add_car(request):
    if request.method == 'POST':
        form = AddCarForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                if 'file_upload' in request.FILES:
                    handle_uploaded_file(request.FILES['file_upload'])
                return redirect('cars:index')
            except Exception as e:
                form.add_error(None, f"Ошибка добавления: {e}")
    else:
        form = AddCarForm()

    return render(request, 'cars/add_car.html', {
        'title': 'Добавить автомобиль',
        'form': form,
        'form_type': 'unbound'
    })


def add_car_model(request):
    if request.method == 'POST':
        form = AddCarModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('cars:index')
    else:
        form = AddCarModelForm()

    return render(request, 'cars/add_car.html', {
        'title': 'Добавить автомобиль (модель)',
        'form': form,
        'form_type': 'model'
    })


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            filepath = handle_uploaded_file(form.cleaned_data['file'])
            return render(request, 'cars/upload_success.html', {
                'title': 'Файл загружен',
                'filepath': filepath
            })
    else:
        form = UploadFileForm()

    return render(request, 'cars/upload_file.html', {
        'title': 'Загрузить файл',
        'form': form
    })


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

def index(request):
    cars = Car.published.all()[:3]

    cars_q = Car.published.filter(Q(brand__icontains='toyota') | Q(year__gte=2025))

    cars_f = Car.published.filter(price__gt=F('year') * 100)

    cars_annotated = Car.published.annotate(title_len=Length('title'), is_new=Value(True)).order_by('-price')[:5]

    cars_values = Car.published.values('brand', 'model_name', 'price', 'category__name')[:5]

    stats = Car.published.aggregate(
        avg_price=Avg('price'),
        max_year=Max('year'),
        min_price=Min('price'),
        total_cars=Count('id')
    )

    categories_with_count = CarCategory.objects.annotate(cars_count=Count('cars')).filter(cars_count__gt=0)

    first_car = Car.published.first()
    last_car = Car.published.order_by('-year').last()
    has_suv_tag = CarTag.objects.filter(slug='suv').exists()
    total_published = Car.published.count()

    context = {
        'title': 'Главная страница',
        'cars': cars,
        'cars_q': cars_q,
        'cars_f': cars_f,
        'cars_annotated': cars_annotated,
        'cars_values': cars_values,
        'stats': stats,
        'categories_with_count': categories_with_count,
        'first_car': first_car,
        'last_car': last_car,
        'has_suv_tag': has_suv_tag,
        'total_published': total_published,
    }
    return render(request, 'cars/index.html', context)

def show_category(request, cat_slug):
    category = get_object_or_404(CarCategory, slug=cat_slug)
    cars = Car.published.filter(category=category)
    return render(request, 'cars/index.html', {
        'title': f'Категория: {category.name}',
        'cars': cars,
        'cat_selected': category.pk
    })


def show_tag(request, tag_slug):
    tag = get_object_or_404(CarTag, slug=tag_slug)
    cars = tag.cars.filter(is_published=Car.Status.PUBLISHED)
    return render(request, 'cars/index.html', {
        'title': f'Тег: {tag.tag}',
        'cars': cars,
        'tag_selected': tag.pk
    })


def cars_list(request):
    min_year = request.GET.get('min_year')
    max_price = request.GET.get('max_price')
    body_type = request.GET.get('body_type')

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

    brands = Car.objects.values_list('brand', flat=True).distinct().order_by('brand')
    body_types = Car.objects.values_list('body_type', flat=True).distinct().order_by('body_type')

    return render(request, 'cars/cars_list.html', {
        'title': 'Список всех автомобилей',
        'cars': cars,
        'brands': brands,
        'body_types': body_types,
        'filter_info': {
            'min_year': min_year or 'не указан',
            'max_price': max_price or 'не указана',
            'body_type': body_type or 'не указан'
        }
    })


def brand(request, brand_slug):
    brand_slug = brand_slug.lower()
    cars = Car.published.filter(brand__iexact=brand_slug)
    if not cars.exists():
        return redirect('cars:cars_list')
    models = cars.values_list('model_name', flat=True).distinct()
    brand_name = cars.first().brand
    return render(request, 'cars/brand.html', {
        'title': f'Автомобили марки {brand_name}',
        'brand': brand_name,
        'cars': cars,
        'models': models,
    })


def car_detail(request, car_slug):
    car = get_object_or_404(Car.published, slug=car_slug)
    return render(request, 'cars/car_detail.html', {
        'title': f'{car.brand} {car.model_name}',
        'car': car,
    })


def vin_info(request, vin_code):
    if not vin_code or len(vin_code) != 17:
        return redirect('cars:cars_list')
    car = Car.objects.filter(vin=vin_code).first()
    wmi = vin_code[:3]
    vds = vin_code[3:9]
    vis = vin_code[9:]
    return render(request, 'cars/vin.html', {
        'title': 'Информация по VIN-коду',
        'vin_code': vin_code,
        'wmi': wmi,
        'vds': vds,
        'vis': vis,
        'car': car,
    })


def brands_list(request):
    brands = Car.objects.filter(is_published=1).values_list('brand', flat=True).distinct().order_by('brand')
    brands_data = []
    for brand in brands:
        count = Car.objects.filter(brand=brand, is_published=1).count()
        brands_data.append({
            'name': brand.lower().replace(' ', '-'),
            'slug': brand.lower().replace(' ', '-'),
            'display': brand,
            'count': count
        })
    return render(request, 'cars/brands_list.html', {
        'title': 'Все марки автомобилей',
        'brands': brands_data,
    })

def categories_list(request):
    categories = CarCategory.objects.annotate(cars_count=Count('cars')).filter(cars_count__gt=0)
    return render(request, 'cars/categories_list.html', {
        'title': 'Все категории',
        'categories': categories,
    })

def tags_list(request):
    tags = CarTag.objects.annotate(cars_count=Count('cars')).filter(cars_count__gt=0)
    return render(request, 'cars/tags_list.html', {
        'title': 'Все теги',
        'tags': tags,
    })