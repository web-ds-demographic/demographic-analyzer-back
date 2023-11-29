from rest_framework import viewsets, status
from rest_framework.response import Response

from main.models import Region, Source, DemographyPrediction
from .serializers import RegionSerializer, SourceSerializer, DemographyPredictionSerializer


class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer


class SourceViewSet(viewsets.ModelViewSet):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer



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