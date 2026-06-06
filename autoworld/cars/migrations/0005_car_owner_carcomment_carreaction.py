# Generated manually for user content, comments and reactions.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cars', '0004_car_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='owner',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='cars',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Автор',
            ),
        ),
        migrations.CreateModel(
            name='CarComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(max_length=1000, verbose_name='Комментарий')),
                ('time_create', models.DateTimeField(auto_now_add=True, verbose_name='Время создания')),
                ('is_active', models.BooleanField(default=True, verbose_name='Показывать')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='car_comments', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='cars.car', verbose_name='Автомобиль')),
            ],
            options={
                'verbose_name': 'Комментарий',
                'verbose_name_plural': 'Комментарии',
                'ordering': ['time_create'],
            },
        ),
        migrations.CreateModel(
            name='CarReaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.SmallIntegerField(choices=[(-1, 'Дизлайк'), (1, 'Лайк')], verbose_name='Оценка')),
                ('time_update', models.DateTimeField(auto_now=True, verbose_name='Время изменения')),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reactions', to='cars.car', verbose_name='Автомобиль')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='car_reactions', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Реакция',
                'verbose_name_plural': 'Реакции',
            },
        ),
        migrations.AddConstraint(
            model_name='carreaction',
            constraint=models.UniqueConstraint(fields=('car', 'user'), name='unique_car_reaction'),
        ),
    ]
