# Generated by Django 4.2.2 on 2023-07-12 23:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('score_up', '0003_remove_letter_letter_text_letter_letter_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='letter',
            name='date_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='letter',
            name='letter_sent',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
