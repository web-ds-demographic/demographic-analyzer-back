from django.db import models


class Region(models.Model):
    region_code = models.CharField(max_length=8)
    region_name = models.CharField(max_length=128)

    def __str__(self):
        return self.region_code


class Source(models.Model):
    source_name = models.CharField(max_length=32)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    def __str__(self):
        return self.source_name


class DemographyEntry(models.Model):
    region = models.CharField("Region code (usually consisting of two letters).", max_length=8)
    source = models.CharField("Source from which this data was obtained.", max_length=32)
    year = models.DateField("The year this record represents the data for.")
    total_population = models.PositiveBigIntegerField("The total number of people lived in this region during this period.", blank=True, null=True)
    births = models.PositiveBigIntegerField("The number of people born in this region during this period.", blank=True, null=True)
    deaths = models.PositiveBigIntegerField("The number of people died in this region during this period.", blank=True, null=True)
    migration = models.BigIntegerField("The number of people left this region during this period minus the number of people entered this region.", blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["region", "source"])
        ]
        unique_together = (("region", "source", "year"),)
    
    def __str__(self):
        return f'Region: {self.region}, Source: {self.source}, Year: {self.year}'


class DemographyPrediction(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    start = models.DateField()
    end = models.DateField()

    def __str__(self):
        return f'DemographyPrediction - Region: {self.region}, Source: {self.source}, Start: {self.start}, End: {self.end}'


