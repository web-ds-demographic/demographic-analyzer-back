from django.db import models


class DemographyEntry(models.Model):
    region = models.CharField("Region code (usually consisting of two letters).", max_length=8, unique=True)
    source = models.CharField("Source from which this data was obtained.", max_length=32, unique=True)
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


class Region(models.Model):
    code = models.OneToOneField(
        DemographyEntry, to_field='region', 
        primary_key=True, on_delete=models.CASCADE, 
        related_name='region_inverse'
    )
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Source(models.Model):
    name = models.OneToOneField(
        DemographyEntry, to_field='source', 
        primary_key=True, on_delete=models.CASCADE, 
        related_name='source_inverse'
    )
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    def __str__(self):
        return self.demography_entry.source


class DemographyPrediction(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    start = models.DateField()
    end = models.DateField()

    def __str__(self):
        return f"DemographyPrediction - Region: {self.region}, Source: {self.source}, Start: {self.start}, End: {self.end}"




# class Region(models.Model):
#     code = models.CharField(max_length=8)
#     name = models.CharField(max_length=128)

#     def __str__(self):
#         return self.name


# class Source(models.Model):
#     name = models.CharField(max_length=32)
#     region = models.ForeignKey(Region, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.name


# # class DemographyEntry(models.Model):
# #     region = models.ForeignKey(Region, on_delete=models.CASCADE)
# #     source = models.ForeignKey(Source, on_delete=models.CASCADE)
# #     year = models.DateField()
# #     total_population = models.PositiveBigIntegerField(blank=True, null=True)
# #     births = models.PositiveBigIntegerField(blank=True, null=True)
# #     deaths = models.PositiveBigIntegerField(blank=True, null=True)
# #     migration = models.BigIntegerField(blank=True, null=True)

# #     class Meta:
# #         indexes = [
# #             models.Index(fields=["region", "source"])
# #         ]
# #         unique_together = (("region", "source", "year"),)


# #     def __str__(self):
# #         return f"DemographyEntry - Region: {self.region}, Source: {self.source}, Year: {self.year}"


# class DemographyPrediction(models.Model):
#     region = models.ForeignKey(Region, on_delete=models.CASCADE)
#     source = models.ForeignKey(Source, on_delete=models.CASCADE)
#     start = models.DateField()
#     end = models.DateField()

#     def __str__(self):
#         return f"DemographyPrediction - Region: {self.region}, Source: {self.source}, Start: {self.start}, End: {self.end}"

# class DemographyEntry(models.Model):
#     region = models.CharField("Region code (usually consisting of two letters).", max_length=8)
#     source = models.CharField("Source from which this data was obtained.", max_length=32)
#     year = models.DateField("The year this record represents the data for.")
#     total_population = models.PositiveBigIntegerField("The total number of people lived in this region during this period.", blank=True, null=True)
#     births = models.PositiveBigIntegerField("The number of people born in this region during this period.", blank=True, null=True)
#     deaths = models.PositiveBigIntegerField("The number of people died in this region during this period.", blank=True, null=True)
#     migration = models.BigIntegerField("The number of people left this region during this period minus the number of people entered this region.", blank=True, null=True)

#     class Meta:
#         indexes = [
#             models.Index(fields=["region", "source"])
#         ]
#         unique_together = (("region", "source", "year"),)
