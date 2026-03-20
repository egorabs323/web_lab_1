from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Car


def index(request):
    cars = Car.published.all()[:3]
    return render(request, 'cars/index.html', {
        'title': 'Главная страница',
        'cars': cars,
    })


def cars_list(request):
    min_year = request.GET.get('min_year')
    max_price = request.GET.get('max_price')
    body_type = request.GET.get('body_type')
    cars = Car.published.all()

    if min_year:
        cars = cars.filter(year__gte=int(min_year))
    if max_price:
        cars = cars.filter(price__lte=float(max_price))
    if body_type:
        cars = cars.filter(body_type=body_type)

    brands = Car.objects.values_list('brand', flat=True).distinct()
    body_types = Car.objects.values_list('body_type', flat=True).distinct()

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