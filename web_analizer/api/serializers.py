from rest_framework import serializers

from main.models import Region, Source, DemographyPrediction


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'

class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = '__all__'

class DemographyPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemographyPrediction
        fields = '__all__'
