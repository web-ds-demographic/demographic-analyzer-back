from rest_framework import serializers

from main.models import Region, Source, DemographyPrediction, DemographyEntry


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
    
    # def validate_source(self, value):
    #     source_name = value.upper()
    #     try:
    #         source = Source.objects.get(source_name=source_name)
    #     except Source.DoesNotExist:
    #         source = Source(source_name=source_name)
    #         source.save()
    #     return source
    
    def create(self, validated_data):
        region = validated_data.pop('region')
        demography_entry = DemographyEntry.objects.create(region=region, **validated_data)
        return demography_entry

class RegionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Region
        fields = ['region_code', 'region_name']


class SourceSerializer(serializers.ModelSerializer):
    min_year = serializers.IntegerField(source='demography_entries__year__min', read_only=True)
    max_year = serializers.IntegerField(source='demography_entries__year__max', read_only=True)

    class Meta:
        model = Source
        fields = ['source_name', 'region', 'min_year', 'max_year']


class DemographyPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemographyPrediction
        fields = '__all__'
