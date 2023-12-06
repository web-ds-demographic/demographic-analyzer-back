from rest_framework import serializers
from django.db.models import TextChoices

from main.models import Region, Source, DemographyEntry
from main.demography_manager import DemographyManager

demography_manager = DemographyManager()


class DemographyEntrySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DemographyEntry
        fields = ['region', 'source', 'year', 'total_population', 'births', 'deaths', 'migration']


    def validate_region(self, value):
        region_code = value.upper()
        try:
            region = Region.objects.get(region_code=region_code)
        except Region.DoesNotExist:
            region = Region(region_code=region_code, region_name='smth')
            region.save()
        return region
    
    def create(self, validated_data):
        region = validated_data.pop('region')
        demography_entry = DemographyEntry.objects.create(region=region, **validated_data)
        return demography_entry

class RegionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Region
        fields = ['region_code', 'region_name']


class SourceSerializer(serializers.ModelSerializer):
    region = RegionSerializer()

    class Meta:
        model = Source
        fields = ['source_name', 'region']


class InputDataPeriodSerializer(serializers.Serializer):
    start = serializers.DateField()
    end = serializers.DateField()


class SourceChoice(TextChoices):
    LOCAL = 'local'
    WORLDBANK = 'worldbank'


class DemographyPredictionSerializer(serializers.Serializer):
    region = serializers.CharField(max_length=2)
    source = serializers.ChoiceField(choices=SourceChoice.choices)
    predict_years_count = serializers.IntegerField()
    inputDataPeriod = InputDataPeriodSerializer()
    
