# Generated by Django 5.1.3 on 2024-12-09 17:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_delete_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='image',
        ),
    ]