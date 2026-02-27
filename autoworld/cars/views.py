from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import redirect
from django.urls import reverse


def index(request):
    if request.GET.get('go') == 'cars':
        return redirect('cars')

    return HttpResponse("""
        <h1>Автомобильный каталог</h1>
        <p>Добро пожаловать в наш автомобильный каталог</p>
        <p>Для просмотра всех автомобилей введите в адресную строку: /cars/</p>
        <p>Для перехода через перенаправление введите: /?go=cars</p>
        <p>Для проверки VIN-кода введите: /vin/1HGBH41JXMN109186/</p>
    """)


def cars(request):
    min_year = request.GET.get('min_year')
    max_price = request.GET.get('max_price')
    body_type = request.GET.get('body_type')
    error = request.GET.get('error')

    filter_info = ""
    if min_year or max_price or body_type:
        filter_info = f"""
            <div style="background: #e7f3ff; padding: 10px; margin: 10px 0;">
                <h4>Активные фильтры:</h4>
                <p>Мин. год: {min_year or 'не указан'}</p>
                <p>Макс. цена: {max_price or 'не указана'}</p>
                <p>Тип кузова: {body_type or 'не указан'}</p>
            </div>
        """

    error_info = ""
    if error == 'invalid_brand':
        error_info = """
            <div style="background: #ffe7e7; padding: 10px; margin: 10px 0; color: #c00;">
                <h4>Неверная марка автомобиля! Вы были перенаправлены на эту страницу.</h4>
            </div>
        """

    return HttpResponse(f"""
        <h1>Список всех автомобилей</h1>
        {error_info}
        {filter_info}
        <p>Для просмотра автомобилей определенной марки введите в адресную строку один из следующих URL:</p>
        <p>/cars/toyota/</p>
        <p>/cars/bmw/</p>
        <p>/cars/mercedes/</p>
        <p>/cars/audi/</p>
        <p>/cars/honda/</p>
        <p>Также можно использовать фильтрацию через GET-параметры:</p>
        <p>/cars/?min_year=2010&max_price=5000000&body_type=sedan</p>
        <p>Для возврата на главную введите: /</p>
    """)


def brand(request, brand_slug):
    valid_brands = ['toyota', 'bmw', 'mercedes', 'audi', 'honda']

    if brand_slug != brand_slug.lower():
        return redirect('brand', brand_slug=brand_slug.lower())

    if brand_slug not in valid_brands:
        return redirect('/cars/?error=invalid_brand')

    return HttpResponse(f"""
        <h1>Автомобили марки {brand_slug.capitalize()}</h1>
        <p>Для просмотра моделей этой марки введите в адресную строку один из следующих URL:</p>
        <p>/cars/{brand_slug}/camry/</p>
        <p>/cars/{brand_slug}/corolla/</p>
        <p>/cars/{brand_slug}/rav4/</p>
        <p>Пример для Toyota:</p>
        <p>/cars/toyota/camry/</p>
        <p>Для возврата к списку марок введите: /cars/</p>
        <p>Для возврата на главную введите: /</p>
    """)


def model(request, brand_slug, model_slug):
    valid_brands = ['toyota', 'bmw', 'mercedes', 'audi', 'honda']

    if brand_slug not in valid_brands:
        return redirect('cars')

    return HttpResponse(f"""
        <h1>Модель {model_slug.capitalize()} марки {brand_slug.capitalize()}</h1>
        <p>Это страница модели {model_slug} марки {brand_slug}</p>
        <p>Для возврата к списку моделей этой марки введите в адресную строку:</p>
        <p>/cars/{brand_slug}/</p>
        <p>Для возврата на главную введите: /</p>
    """)

def page_not_found(request, exception):
    return HttpResponseNotFound("""
        <h1>Страница не найдена</h1>
        <p>Проверьте правильность URL или введите в адресную строку: /cars/</p>
        <p>Для возврата на главную введите: /</p>
    """)
def vin_info(request, vin_code):
    if not vin_code or len(vin_code) != 17:
        return redirect('cars')

    return HttpResponse(f"""
        <h1>Информация по VIN-коду</h1>
        <p>VIN: {vin_code}</p>
        <p>Длина: {len(vin_code)} символов</p>
        <p>Первые 3 символа (WMI): {vin_code[:3]} - Код производителя</p>
        <p>Символы 4-9 (VDS): {vin_code[3:9]} - Описание автомобиля</p>
        <p>Символы 10-17 (VIS): {vin_code[9:]} - Индивидуальная информация</p>
        <p>Для возврата к каталогу введите: /cars/</p>
        <p>Для возврата на главную введите: /</p>
    """)