import os
import pandas as pd
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from main.demography_manager import DemographyManager
from main.core_models import TimePeriod
from main.models import Region, Source
from .serializers import RegionSerializer, SourceSerializer, DemographyPredictionSerializer

demography_manager = DemographyManager()


class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

    def list(self, request):
        regions = demography_manager.get_regions()

        data = []
        for region in regions:
            Region.objects.get_or_create(region_code=region.code, region_name=region.name)
            data.append({
                'code': region.code,
                'name': region.name,
                'sources': region.sources
            })
        return Response(data)


class SourceViewSet(viewsets.ModelViewSet):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer

    def list(self, request):
        """выводит список ресурсов"""
        regions = demography_manager.get_regions()
        sources_dict = {}

        for region in regions:
            region_obj, created = Region.objects.get_or_create(
                region_code=region.code,
                defaults={'region_name': region.name},
            )

            for source_name in region.sources:
                if source_name not in sources_dict:
                    sources_dict[source_name] = []
                sources_dict[source_name].append(region_obj)

        for source_name, regions in sources_dict.items():
            source_obj, created = Source.objects.get_or_create(
                source_name=source_name,
            )
            source_obj.region.set(regions)

        data = [{'source_name': source, 'regions': [region.region_code for region in regions]} for source, regions in sources_dict.items()]
        return Response(data)
    

    def retrieve(
            self, 
            request,
            region_code,
            source_name
    ):
        """На запрос api/source/<region_code>/<source_name>/ 
        возвращет min max данных в источнике"""
        print(f'{region_code=}')

        if not region_code or not source_name:
            raise ValueError('Region code and source name required')
        
        
        available_period = demography_manager.get_availible_period(region=region_code, source=source_name)
        if available_period is None:
            return Response({
                'error': f'No available period found for the given {region_code} and {source_name}'
            }, status=404)
        return Response({
            'min': available_period.start,
            'max': available_period.end  
        })
    
    

class DemographyPredictionView(GenericAPIView):
    serializer_class = DemographyPredictionSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pred_method = demography_manager.predict(
            region=serializer.validated_data['region'],
            source=serializer.validated_data['source'],
            predict_years_count=serializer.validated_data['predict_years_count'],
            input_period=TimePeriod(
                start=serializer.validated_data['inputDataPeriod']['start'],
                end=serializer.validated_data['inputDataPeriod']['end'],
            )
        )
        if pred_method is None:
            return Response({'detail': 'no data'}, status=404)
        data = demography_manager.pd_data_to_json(pred_method)
        return Response(data)
