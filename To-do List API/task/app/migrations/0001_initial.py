# Generated by Django 5.1.3 on 2025-01-24 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Todo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64)),
                ('description', models.CharField(max_length=1024)),
                ('goal_set_date', models.DateField()),
                ('set_to_complete', models.DateField()),
                ('is_completed', models.BooleanField()),
            ],
        ),
    ]
