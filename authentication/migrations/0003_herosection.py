# Generated by Django 4.2.1 on 2025-01-30 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_place_booking_trend_place_revenue_forecast_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeroSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_index', models.IntegerField(default=0)),
                ('hero_text', models.CharField(default='Choose Your Purpose: Culinary Delights, Thrilling Sports, Cultural Journeys, and More!', max_length=255)),
                ('image1', models.ImageField(blank=True, null=True, upload_to='hero_images/')),
                ('image2', models.ImageField(blank=True, null=True, upload_to='hero_images/')),
                ('image3', models.ImageField(blank=True, null=True, upload_to='hero_images/')),
            ],
        ),
    ]
