# Generated by Django 3.2.16 on 2022-11-11 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assetmgr', '0016_asset_transcript'),
    ]

    operations = [
        migrations.AlterField(
            model_name='source',
            name='url',
            field=models.TextField(),
        ),
    ]
