# Generated by Django 5.0 on 2023-12-08 22:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('airport', '0002_rename_sourse_route_source'),
        ('order', '0002_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ticket',
            options={'ordering': ['row', 'seat']},
        ),
        migrations.AlterUniqueTogether(
            name='ticket',
            unique_together={('flight', 'row', 'seat')},
        ),
    ]
