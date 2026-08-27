from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import WorkOutViewSet, BodyMeasurementViewSet, ProfileViewSet, TrainerListView, MyTraineesView

router = DefaultRouter()
router.register(r'workouts', WorkOutViewSet, basename='workout')
router.register(r'bodymeasurements', BodyMeasurementViewSet, basename='bodymeasurement')
router.register(r'profile', ProfileViewSet, basename='profile')

urlpatterns = router.urls + [
    path('trainers/', TrainerListView.as_view(), name='trainer_list'),
    path('my-trainees/', MyTraineesView.as_view(), name='my_trainees'),
]