from rest_framework.routers import DefaultRouter
from .views import WorkOutViewSet, BodyMeasurementViewSet, ProfileViewSet

router = DefaultRouter()
router.register(r'workouts', WorkOutViewSet, basename='workout')
router.register(r'bodymeasurements', BodyMeasurementViewSet, basename='bodymeasurement')
router.register(r'profile', ProfileViewSet, basename='profile')

urlpatterns = router.urls