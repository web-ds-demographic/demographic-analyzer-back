from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RegionViewSet, SourceViewSet, DemographyPredictionView

router = DefaultRouter()

router.register('regions', RegionViewSet, basename='regions')
router.register('sources', SourceViewSet, basename='sources')

urlpatterns = [
    path('', include(router.urls)),
    path('source/<str:region_code>/<str:source_name>/', SourceViewSet.as_view({'get': 'retrieve'}), name='source-detail'),
    path('prediction/', DemographyPredictionView.as_view(), name='prediction'),
]
