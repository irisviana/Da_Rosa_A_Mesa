# Generated by Django 3.2.3 on 2021-06-24 23:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='product_pic',
            field=models.ImageField(default='static/productImages/img_default.png', upload_to='static/productImages/'),
        ),
    ]