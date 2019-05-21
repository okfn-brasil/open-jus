# Generated by Django 2.1.5 on 2019-02-28 01:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_add_appeas_field_to_tjsp_court_order_model'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CourtOrderTJSP',
            new_name='CourtOrderESAJ',
        ),
        migrations.RemoveIndex(
            model_name='courtorderesaj',
            name='core_courto_decisio_69fb5e_idx',
        ),
        migrations.RemoveIndex(
            model_name='courtorderesaj',
            name='core_courto_number_5adf2b_idx',
        ),
        migrations.AddIndex(
            model_name='courtorderesaj',
            index=models.Index(fields=['decision_date'], name='core_courto_decisio_7960cc_idx'),
        ),
        migrations.AddIndex(
            model_name='courtorderesaj',
            index=models.Index(fields=['number'], name='core_courto_number_4d976b_idx'),
        ),
    ]