from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RegionViewSet, SourceViewSet, DemographyPredictionViewSet, DemographyEntryViewSet

router = DefaultRouter()

router.register(r'regions', RegionViewSet, basename='regions')
router.register(r'sources', SourceViewSet, basename='sources')
router.register(r'predictions', DemographyPredictionViewSet, basename='predictions')
router.register(r'entry', DemographyEntryViewSet, basename='entry')

urlpatterns = [
    path('', include(router.urls)),
    path('source/<int:pk>/', SourceViewSet.as_view({'get': 'retrieve'}), name='source-detail'),
]
