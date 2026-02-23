from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import redirect
from django.urls import reverse

def index(request):
    return HttpResponse("""
        <h1>Автомобильный каталог</h1>
        <p>Добро пожаловать в наш автомобильный каталог</p>
        <p>Для просмотра всех автомобилей введите в адресную строку: /cars/</p>
    """)

def cars(request):
    return HttpResponse("""
        <h1>Список всех автомобилей</h1>
        <p>Для просмотра автомобилей определенной марки введите в адресную строку один из следующих URL:</p>
        <p>/cars/toyota/</p>
        <p>/cars/bmw/</p>
        <p>/cars/mercedes/</p>
        <p>/cars/audi/</p>
        <p>/cars/honda/</p>
        <p>Также можно использовать фильтрацию через GET-параметры:</p>
        <p>/cars/?min_year=2010&max_price=5000000&body_type=sedan</p>
    """)


def brand(request, brand_slug):
    valid_brands = ['toyota', 'bmw', 'mercedes', 'audi', 'honda']

    if brand_slug not in valid_brands:
        return HttpResponseNotFound("""
            <h1>Страница не найдена</h1>
            <p>Неверная марка автомобиля. Доступные марки:</p>
            <p>/cars/toyota/</p>
            <p>/cars/bmw/</p>
            <p>/cars/mercedes/</p>
            <p>/cars/audi/</p>
            <p>/cars/honda/</p>
        """)

    return HttpResponse(f"""
        <h1>Автомобили марки {brand_slug.capitalize()}</h1>
        <p>Для просмотра моделей этой марки введите в адресную строку один из следующих URL:</p>
        <p>/cars/{brand_slug}/camry/</p>
        <p>/cars/{brand_slug}/corolla/</p>
        <p>/cars/{brand_slug}/rav4/</p>
        <p>Пример для Toyota:</p>
        <p>/cars/toyota/camry/</p>
    """)


def model(request, brand_slug, model_slug):
    valid_brands = ['toyota', 'bmw', 'mercedes', 'audi', 'honda']

    if brand_slug not in valid_brands:
        return HttpResponseNotFound("""
            <h1>Страница не найдена</h1>
            <p>Неверная марка автомобиля. Доступные марки:</p>
            <p>/cars/toyota/</p>
            <p>/cars/bmw/</p>
            <p>/cars/mercedes/</p>
            <p>/cars/audi/</p>
            <p>/cars/honda/</p>
        """)

    return HttpResponse(f"""
        <h1>Модель {model_slug.capitalize()} марки {brand_slug.capitalize()}</h1>
        <p>Это страница модели {model_slug} марки {brand_slug}</p>
        <p>Для возврата к списку моделей этой марки введите в адресную строку:</p>
        <p>/cars/{brand_slug}/</p>
    """)

def page_not_found(request, exception):
    return HttpResponseNotFound("""
        <h1>Страница не найдена</h1>
        <p>Проверьте правильность URL или <a href="/cars/">вернитесь к выбору марок</a></p>
    """)

def vin_info(request, vin_code):
    # Здесь может быть логика проверки VIN-кода
    return HttpResponse(f"<h1>Информация по VIN-коду</h1><p>VIN: {vin_code}</p>")