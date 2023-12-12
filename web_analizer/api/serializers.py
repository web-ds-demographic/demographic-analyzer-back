from rest_framework import serializers
from django.db.models import TextChoices

from main.models import Region, Source, DemographyEntry
from main.demography_manager import DemographyManager

demography_manager = DemographyManager()


class DemographyEntrySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DemographyEntry
        fields = ['region', 'source', 'year', 'total_population', 'births', 'deaths', 'migration']


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
    
