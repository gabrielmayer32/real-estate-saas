# Generated by Django 5.0.6 on 2024-06-23 12:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0004_property_interior_surface_numeric_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='property',
            old_name='interior_surface_numeric',
            new_name='interior_surface_clean',
        ),
    ]
