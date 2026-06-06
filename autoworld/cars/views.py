import os
import uuid
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login
from django.db.models import Count
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

from .forms import AddCarForm, AddCarModelForm, CarCommentForm, UploadFileForm, VinCheckForm
from .models import Car, CarCategory, CarComment, CarReaction, CarTag


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


class OwnerOrPermissionRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        car = self.get_object()
        return car.owner_id == self.request.user.id

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect_to_login(
                self.request.get_full_path(),
                self.get_login_url(),
                self.get_redirect_field_name(),
            )
        return super().handle_no_permission()


class CommentAuthorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    model = CarComment
    pk_url_kwarg = 'comment_pk'
    raise_exception = True

    def test_func(self):
        comment = self.get_object()
        return comment.author_id == self.request.user.id

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect_to_login(
                self.request.get_full_path(),
                self.get_login_url(),
                self.get_redirect_field_name(),
            )
        return super().handle_no_permission()


class CarsHome(DataMixin, ListView):
    template_name = 'cars/index.html'
    title_page = 'Главная страница'

    def get_queryset(self):
        return Car.published.select_related('category', 'engine').prefetch_related('tags')

class AddCarPage(PermissionRequiredMixin, DataMixin, View):
    permission_required = 'cars.add_car'
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


class AddCarModelPage(LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddCarModelForm
    template_name = 'cars/add_car.html'
    success_url = reverse_lazy('cars:index')
    title_page = 'Добавить автомобиль'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Автомобиль добавлен.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, form_type='model')


class UpdateCarPage(OwnerOrPermissionRequiredMixin, DataMixin, UpdateView):
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


class DeleteCarPage(OwnerOrPermissionRequiredMixin, DataMixin, DeleteView):
    model = Car
    template_name = 'cars/car_confirm_delete.html'
    slug_url_kwarg = 'car_slug'
    success_url = reverse_lazy('cars:cars_list')
    title_page = 'Удаление автомобиля'


class UploadFilePage(LoginRequiredMixin, DataMixin, FormView):
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
        return Car.published.select_related('category', 'engine', 'owner').prefetch_related('tags', 'comments__author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_reaction = None
        if self.request.user.is_authenticated:
            user_reaction = self.object.reactions.filter(user=self.request.user).first()

        return self.get_mixin_context(
            context,
            title=f'{self.object.brand} {self.object.model_name}',
            comment_form=CarCommentForm(),
            comments=self.object.comments.filter(is_active=True).select_related('author'),
            likes_count=self.object.reactions.filter(value=CarReaction.Value.LIKE).count(),
            dislikes_count=self.object.reactions.filter(value=CarReaction.Value.DISLIKE).count(),
            user_reaction=user_reaction,
            can_edit_car=(
                self.request.user.is_authenticated and
                self.object.owner_id == self.request.user.id
            ),
            can_delete_car=(
                self.request.user.is_authenticated and
                self.object.owner_id == self.request.user.id
            ),
        )


class AddCommentPage(LoginRequiredMixin, View):
    def post(self, request, car_slug):
        car = get_object_or_404(Car.published, slug=car_slug)
        form = CarCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.car = car
            comment.author = request.user
            comment.save()
            messages.success(request, 'Комментарий добавлен.')
        else:
            messages.error(request, 'Не удалось добавить комментарий.')
        return redirect(car.get_absolute_url())


class UpdateCommentPage(CommentAuthorRequiredMixin, DataMixin, UpdateView):
    form_class = CarCommentForm
    template_name = 'cars/comment_form.html'
    title_page = 'Редактирование комментария'

    def get_success_url(self):
        messages.success(self.request, 'Комментарий обновлен.')
        return self.object.car.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, car=self.object.car)


class DeleteCommentPage(CommentAuthorRequiredMixin, DataMixin, DeleteView):
    template_name = 'cars/comment_confirm_delete.html'
    title_page = 'Удаление комментария'

    def get_success_url(self):
        messages.success(self.request, 'Комментарий удален.')
        return self.object.car.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, car=self.object.car)


class ToggleReactionPage(LoginRequiredMixin, View):
    reaction_values = {
        'like': CarReaction.Value.LIKE,
        'dislike': CarReaction.Value.DISLIKE,
    }

    def post(self, request, car_slug):
        car = get_object_or_404(Car.published, slug=car_slug)
        reaction_value = self.reaction_values.get(request.POST.get('reaction'))

        if reaction_value is None:
            messages.error(request, 'Неизвестная реакция.')
            return redirect(car.get_absolute_url())

        reaction, created = CarReaction.objects.get_or_create(
            car=car,
            user=request.user,
            defaults={'value': reaction_value},
        )

        if not created and reaction.value == reaction_value:
            reaction.delete()
            messages.info(request, 'Реакция удалена.')
        else:
            reaction.value = reaction_value
            reaction.save(update_fields=['value', 'time_update'])
            messages.success(request, 'Реакция сохранена.')

        return redirect(car.get_absolute_url())


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
    title_page = 'Проверка VIN-кода'

    def post(self, request, *args, **kwargs):
        form = VinCheckForm(request.POST)
        if form.is_valid():
            return self.render_to_response(self.get_vin_context(form.cleaned_data['vin_code'], form))
        return self.render_to_response(self.get_mixin_context({}, form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vin_code = self.kwargs.get('vin_code') or self.request.GET.get('vin_code')
        if not vin_code:
            return self.get_mixin_context(context, form=VinCheckForm())

        form = VinCheckForm({'vin_code': vin_code})
        if not form.is_valid():
            return self.get_mixin_context(context, form=form)

        return self.get_vin_context(form.cleaned_data['vin_code'], form, context)

    def get_vin_context(self, vin_code, form, context=None):
        context = context or {}
        return self.get_mixin_context(
            context,
            form=form,
            vin_code=vin_code,
            wmi=vin_code[:3],
            vds=vin_code[3:9],
            vis=vin_code[9:],
            car=Car.objects.filter(vin=vin_code).first(),
            checked=True,
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
