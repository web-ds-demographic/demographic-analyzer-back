from rest_framework import serializers

from main.models import Region, Source, DemographyPrediction, DemographyEntry


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['code', 'name']

class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = '__all__'

class DemographyPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemographyEntry
        fields = '__all__'
