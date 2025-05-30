# Generated by Django 5.1.2 on 2025-05-06 09:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="JobProgress",
            fields=[
                (
                    "task_id",
                    models.CharField(max_length=36, primary_key=True, serialize=False),
                ),
                ("total", models.IntegerField()),
                ("processed", models.IntegerField(default=0)),
                ("started", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
