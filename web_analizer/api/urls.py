from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RegionViewSet, SourceViewSet, DemographyPredictionViewSet

router = DefaultRouter()

router.register(r'regions', RegionViewSet, basename='regions')
router.register(r'sources', SourceViewSet, basename='sources')
router.register(r'predictions', DemographyPredictionViewSet, basename='predictions')

urlpatterns = [
    path('', include(router.urls)),
]
