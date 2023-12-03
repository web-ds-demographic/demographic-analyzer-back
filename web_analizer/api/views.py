import os
import pandas as pd
from django.db import models
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from main.demography_manager import DemographyManager
from main.models import Region, Source, DemographyPrediction, DemographyEntry
from .serializers import RegionSerializer, SourceSerializer, DemographyPredictionSerializer, DemographyEntrySerializer
from main import settings


class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

    def list(self, request):
        demography_manager = DemographyManager()
        regions = demography_manager.get_regions()

        data = []
        for region in regions:
            data.append({
                'code': region.code,
                'name': region.name,
                'sources': region.sources
            })
        return Response(data)


class SourceViewSet(viewsets.ModelViewSet):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer

    def retrieve(self, request, *args, **kwargs):
        """при запросе на api/source/<pk>/?region=<region_code>&source=<source_name> 
        возвращает min max year"""
        region_code = self.request.query_params.get('region')
        source_name = self.request.query_params.get('source')
        
        if region_code and source_name:
            demography_entries = DemographyEntry.objects.filter(region__region_code=region_code, source__source_name=source_name)
            
            min_year = demography_entries.aggregate(min_year=models.Min('year'))['min_year']
            max_year = demography_entries.aggregate(max_year=models.Max('year'))['max_year']
    
            data = {
                'min': min_year.strftime('%Y') if min_year else 'N/A',
                'max': max_year.strftime('%Y') if max_year else 'N/A'
            }
    
            return Response(data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        

class DemographyEntryViewSet(viewsets.ModelViewSet):
    pass


class DemographyPredictionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DemographyPrediction.objects.all()
    serializer_class = DemographyPredictionSerializer

    def create(self, request, *args, **kwargs):
        demography_manager = DemographyManager()
        region = request.data.get('region')
        source = request.data.get('source')
        inputDataPeriod = request.data.get('inputDataPeriod')

        if not all([region, source, inputDataPeriod]):
            return Response("Missing required data", status=status.HTTP_400_BAD_REQUEST)

        start_year = int(inputDataPeriod.get('start'))
        end_year = int(inputDataPeriod.get('end'))

        demography_data = demography_manager._get_data(region, source, inputDataPeriod)

        missing_years = [year for year in range(start_year, end_year+1) if year not in demography_data.index]

        if missing_years:
            for year in missing_years:
                data = demography_manager._get_and_cache_data(region, source, year)
                DemographyPrediction.objects.create(region=region, source=source, year=year, prediction=data)

        file_path = os.path.join(settings.AppSettings, f"{region}__{source}.csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)

        demography_data = DemographyPrediction.objects.filter(region=region, source=source,
                                                          year__gte=start_year, year__lte=end_year)

        serializer = self.get_serializer(demography_data, many=True)
        return Response(serializer.data)