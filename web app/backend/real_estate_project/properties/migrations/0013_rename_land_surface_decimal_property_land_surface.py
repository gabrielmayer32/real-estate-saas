# Generated by Django 5.0.6 on 2024-06-26 09:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0012_remove_property_land_surface_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='property',
            old_name='land_surface_decimal',
            new_name='land_surface',
        ),
    ]
