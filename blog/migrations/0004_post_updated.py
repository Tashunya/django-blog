# Generated by Django 2.2.5 on 2019-10-01 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20190906_1551'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
