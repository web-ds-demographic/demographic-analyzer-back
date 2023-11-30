from django.db import models
from rest_framework import viewsets, status
from rest_framework.response import Response

from main.models import Region, Source, DemographyPrediction, DemographyEntry
from .serializers import RegionSerializer, SourceSerializer, DemographyPredictionSerializer


class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

    def list(self, request, *args, **kwargs):
        regions = Region.objects.all()
        serialized_regions = RegionSerializer(regions, many=True).data

        result = []
        for serialized_region in serialized_regions:
            region_code = serialized_region['code']
            region_name = serialized_region['name']
            sources = Source.objects.filter(
                region__code=region_code).values_list(
                    'name', flat=True
                )

            result.append({
                "code": region_code,
                "name": region_name,
                "sources": sources
            })

        return Response(result)


class SourceViewSet(viewsets.ModelViewSet):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer

    def retrieve(self, request, *args, **kwargs):
        """при запросе на api/source/<pk>/?region=<region_code>&source=<source_name> 
        возвращает min max year"""
        region_code = self.request.query_params.get('region')
        source_name = self.request.query_params.get('source')
        
        if region_code and source_name:
            demography_entries = DemographyEntry.objects.filter(region=region_code, source=source_name)
            
            min_year = demography_entries.aggregate(min_year=models.Min('year'))['min_year']
            max_year = demography_entries.aggregate(max_year=models.Max('year'))['max_year']
    
            data = {
                'min': min_year.strftime('%Y') if min_year else 'N/A',
                'max': max_year.strftime('%Y') if max_year else 'N/A'
            }
    
            return Response(data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class DemographyPredictionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DemographyPrediction.objects.all()
    serializer_class = DemographyPredictionSerializer

    def post(self, request, *args, **kwargs):
        region = request.data.get('region')
        source = request.data.get('source')
        inputDataPeriod = request.data.get('inputDataPeriod')

        if not all([region, source, inputDataPeriod]):
            return Response("Missing required data", status=status.HTTP_400_BAD_REQUEST)

        start_year = int(inputDataPeriod.get('start'))
        end_year = int(inputDataPeriod.get('end'))

        predictions = DemographyPrediction.objects.filter(region=region, source=source,
                                                          start__year__gte=start_year, end__year__lte=end_year)

        data = self.get_serializer(predictions, many=True).data

        return Response(data)