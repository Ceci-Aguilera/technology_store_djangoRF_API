# Generated by Django 2.2.8 on 2021-07-03 19:02

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store_app', '0003_auto_20210702_0124'),
    ]

    operations = [
        migrations.CreateModel(
            name='ColorVariation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nickname', models.CharField(max_length=256)),
                ('color_in_hex', models.CharField(default='#000000', max_length=256, validators=[django.core.validators.RegexValidator('^#(?:[0-9a-fA-F]{3}){1,2}$', 'only valid hex color code is accepted')])),
            ],
        ),
        migrations.RemoveField(
            model_name='order',
            name='items',
        ),
        migrations.AddField(
            model_name='cartitem',
            name='order',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='cart_items_set', to='store_app.Order'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productvariation',
            name='color_variations',
            field=models.ManyToManyField(to='store_app.ColorVariation'),
        ),
    ]