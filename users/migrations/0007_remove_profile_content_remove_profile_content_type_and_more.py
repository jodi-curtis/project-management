# Generated by Django 5.1.3 on 2024-12-09 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_remove_profile_image_profile_content_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='content',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='content_type',
        ),
        migrations.AddField(
            model_name='profile',
            name='image',
            field=models.ImageField(default='default.jpg', upload_to='profile_pics'),
        ),
    ]