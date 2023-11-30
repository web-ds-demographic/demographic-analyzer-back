from rest_framework import serializers

from main.models import Region, Source, DemographyPrediction, DemographyEntry


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['code', 'name']


class SourceSerializer(serializers.ModelSerializer):
    min_year = serializers.IntegerField(source='demography_entries__year__min', read_only=True)
    max_year = serializers.IntegerField(source='demography_entries__year__max', read_only=True)

    class Meta:
        model = Source
        fields = ['name', 'region', 'min_year', 'max_year']


class DemographyPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemographyPrediction
        fields = '__all__'
