# Generated by Django 5.1.3 on 2024-12-09 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_profile_job_role'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='image',
        ),
        migrations.AddField(
            model_name='profile',
            name='content',
            field=models.BinaryField(default=b''),
        ),
        migrations.AddField(
            model_name='profile',
            name='content_type',
            field=models.CharField(default='image/jpeg', max_length=100),
        ),
    ]
