from django.shortcuts import render, redirect
from django.urls import reverse

VALID_BRANDS = [
    {'name': 'toyota', 'display': 'Toyota'},
    {'name': 'bmw', 'display': 'BMW'},
    {'name': 'mercedes', 'display': 'Mercedes'},
    {'name': 'audi', 'display': 'Audi'},
    {'name': 'honda', 'display': 'Honda'},
]

def index(request):
    return render(request, 'cars/index.html', {
        'title': 'Главная страница',
    })

def cars_list(request):
    min_year = request.GET.get('min_year')
    max_price = request.GET.get('max_price')
    body_type = request.GET.get('body_type')
    error = request.GET.get('error')

    filter_info = {
        'min_year': min_year or 'не указан',
        'max_price': max_price or 'не указана',
        'body_type': body_type or 'не указан'
    }

    error_info = None
    if error == 'invalid_brand':
        error_info = 'Неверная марка автомобиля! Вы были перенаправлены на эту страницу.'

    return render(request, 'cars/cars_list.html', {
        'title': 'Список всех автомобилей',
        'filter_info': filter_info,
        'error_info': error_info,
        'brands': VALID_BRANDS,
    })

def brand(request, brand_slug):
    brand_slug = brand_slug.lower()
    brand_obj = next((b for b in VALID_BRANDS if b['name'] == brand_slug), None)

    if not brand_obj:
        return redirect('cars:cars_list')

    models = {
        'toyota': ['Camry', 'Corolla', 'RAV4'],
        'bmw': ['X5', '3 Series', 'i8'],
        'mercedes': ['C-Class', 'E-Class', 'GLC'],
        'audi': ['A4', 'Q5', 'R8'],
        'honda': ['Civic', 'Accord', 'CR-V'],
    }.get(brand_slug, [])

    return render(request, 'cars/brand.html',  {
        'title': f'Автомобили марки {brand_obj["display"]}',
        'brand': brand_obj,
        'models': models,
    })

def model(request, brand_slug, model_slug):
    brand_slug = brand_slug.lower()
    brand_obj = next((b for b in VALID_BRANDS if b['name'] == brand_slug), None)
    if not brand_obj:
        return redirect('cars:cars_list')

    return render(request, 'cars/model.html', {
        'title': f'Модель {model_slug.capitalize()} марки {brand_obj["display"]}',
        'brand': brand_obj,
        'model': model_slug.capitalize(),
    })

def vin_info(request, vin_code):
    if not vin_code or len(vin_code) != 17:
        return redirect('cars:cars_list')

    wmi = vin_code[:3]
    vds = vin_code[3:9]
    vis = vin_code[9:]

    return render(request, 'cars/vin.html', {
        'title': 'Информация по VIN-коду',
        'vin_code': vin_code,
        'wmi': wmi,
        'vds': vds,
        'vis': vis,
    })