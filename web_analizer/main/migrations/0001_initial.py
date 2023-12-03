# Generated by Django 4.2.7 on 2023-12-03 14:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Region",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("region_code", models.CharField(max_length=8)),
                ("region_name", models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name="Source",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("source_name", models.CharField(max_length=32)),
                (
                    "region",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="main.region"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DemographyPrediction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("start", models.DateField()),
                ("end", models.DateField()),
                (
                    "region",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="main.region"
                    ),
                ),
                (
                    "source",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="main.source"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DemographyEntry",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "region",
                    models.CharField(
                        max_length=8,
                        verbose_name="Region code (usually consisting of two letters).",
                    ),
                ),
                (
                    "source",
                    models.CharField(
                        max_length=32,
                        verbose_name="Source from which this data was obtained.",
                    ),
                ),
                (
                    "year",
                    models.DateField(
                        verbose_name="The year this record represents the data for."
                    ),
                ),
                (
                    "total_population",
                    models.PositiveBigIntegerField(
                        blank=True,
                        null=True,
                        verbose_name="The total number of people lived in this region during this period.",
                    ),
                ),
                (
                    "births",
                    models.PositiveBigIntegerField(
                        blank=True,
                        null=True,
                        verbose_name="The number of people born in this region during this period.",
                    ),
                ),
                (
                    "deaths",
                    models.PositiveBigIntegerField(
                        blank=True,
                        null=True,
                        verbose_name="The number of people died in this region during this period.",
                    ),
                ),
                (
                    "migration",
                    models.BigIntegerField(
                        blank=True,
                        null=True,
                        verbose_name="The number of people left this region during this period minus the number of people entered this region.",
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["region", "source"],
                        name="main_demogr_region_df88a4_idx",
                    )
                ],
                "unique_together": {("region", "source", "year")},
            },
        ),
    ]
