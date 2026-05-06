from django import forms
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from .models import Car, CarCategory, CarTag, CarEngine

@deconstructible
class RussianVinValidator:
    """Валидатор: только латинские буквы, цифры (для VIN)"""
    ALLOWED_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    def __init__(self, message=None):
        self.message = message or "VIN-код должен содержать только латинские буквы и цифры"

    def __call__(self, value):
        if not set(value.upper()).issubset(set(self.ALLOWED_CHARS)):
            raise ValidationError(self.message)


class AddCarForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        min_length=5,
        label="Название",
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        validators=[MinLengthValidator(5, message="Минимум 5 символов")],
        error_messages={
            'required': 'Название обязательно',
            'min_length': 'Слишком короткое название'
        }
    )

    slug = forms.SlugField(
        max_length=255,
        label="URL-слаг",
        validators=[
            MinLengthValidator(3, message="Минимум 3 символа"),
            MaxLengthValidator(100, message="Максимум 100 символов")
        ]
    )

    brand = forms.CharField(
        max_length=100,
        label="Марка",
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )

    model_name = forms.CharField(
        max_length=100,
        label="Модель",
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )

    vin = forms.CharField(
        max_length=17,
        min_length=17,
        label="VIN-код",
        widget=forms.TextInput(attrs={'class': 'form-input', 'maxlength': '17'}),
        validators=[RussianVinValidator()],
        error_messages={
            'min_length': 'VIN-код должен содержать ровно 17 символов',
            'max_length': 'VIN-код должен содержать ровно 17 символов'
        }
    )

    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Цена (₽)",
        min_value=0
    )

    year = forms.IntegerField(
        label="Год выпуска",
        min_value=1900,
        max_value=2030
    )

    body_type = forms.CharField(
        max_length=50,
        label="Тип кузова",
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )

    description = forms.CharField(
        required=False,
        label="Описание",
        widget=forms.Textarea(attrs={'cols': 60, 'rows': 5})
    )

    is_published = forms.BooleanField(
        required=False,
        label="Опубликовано",
        initial=True
    )

    category = forms.ModelChoiceField(
        queryset=CarCategory.objects.all(),
        label="Категория",
        empty_label="Выберите категорию"
    )

    engine = forms.ModelChoiceField(
        queryset=CarEngine.objects.all(),
        required=False,
        label="Двигатель",
        empty_label="Не указан"
    )

    tags = forms.ModelMultipleChoiceField(
        queryset=CarTag.objects.all(),
        required=False,
        label="Теги",
        widget=forms.CheckboxSelectMultiple
    )

    file_upload = forms.FileField(
        required=False,
        label="Прикрепить файл"
    )

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 100:
            raise ValidationError('Название не должно превышать 100 символов')
        return title

class AddCarModelForm(forms.ModelForm):
    title = forms.CharField(
        max_length=255,
        min_length=5,
        label="Название",
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        error_messages={
            'required': 'Название обязательно',
            'min_length': 'Минимум 5 символов'
        }
    )

    category = forms.ModelChoiceField(
        queryset=CarCategory.objects.all(),
        label="Категория",
        empty_label="Выберите категорию"
    )

    engine = forms.ModelChoiceField(
        queryset=CarEngine.objects.all(),
        required=False,
        label="Двигатель",
        empty_label="Не указан"
    )

    tags = forms.ModelMultipleChoiceField(
        queryset=CarTag.objects.all(),
        required=False,
        label="Теги",
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Car
        fields = [
            'title', 'slug', 'brand', 'model_name', 'year',
            'price', 'body_type', 'vin', 'description',
            'is_published', 'category', 'engine', 'tags', 'photo'
        ]
        labels = {
            'slug': 'URL-слаг',
            'model_name': 'Модель',
            'body_type': 'Тип кузова',
        }
        widgets = {
            'description': forms.Textarea(attrs={'cols': 60, 'rows': 5}),
            'vin': forms.TextInput(attrs={'maxlength': '17'}),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 100:
            raise ValidationError('Название не должно превышать 100 символов')
        return title

    # Валидатор для VIN-кода
    def clean_vin(self):
        vin = self.cleaned_data['vin'].upper()
        if len(vin) != 17:
            raise ValidationError('VIN-код должен содержать ровно 17 символов')
        if not set(vin).issubset(set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")):
            raise ValidationError('VIN-код должен содержать только латинские буквы и цифры')
        return vin

class UploadFileForm(forms.Form):
    file = forms.FileField(label="Выберите файл")
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file and file.size > 10 * 1024 * 1024:
            raise ValidationError("Файл слишком большой (макс. 10 МБ)")
        return file

class UploadImageForm(forms.Form):
    image = forms.ImageField(label="Выберите изображение")